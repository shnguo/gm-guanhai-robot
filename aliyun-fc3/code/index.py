# -*- coding: utf-8 -*-

import logging
import datetime
from odps import ODPS
import os
from templates import voc_template, voc_summary_template, commentcls_template,voc_classification_template
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks.manager import get_openai_callback
import tiktoken
from pymodels import Optimization_List,Classification_Result
from loguru import logger
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True, verbose=True)
from llms import llm_factory, llm_context_length
import sys
import en_core_web_sm
from pydantic import BaseModel, Field
from typing import List, Optional, Union
import numpy as np

sys.path.append("..")
enc = tiktoken.encoding_for_model("gpt-4")
nlp = en_core_web_sm.load()


def handler(event, context):
    logger = logging.getLogger()
    logger.info(event)
    return event


def emoji_handler(event, context):
    logger = logging.getLogger()
    # logger.info(event)
    data = eval(event.decode("utf-8").replace("false", "False"))[0]
    logger.info(data["body"])
    return datetime.datetime.now()


def get_odps_data(sql):
    o = ODPS(
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
        project="gmods",
        endpoint="http://service.cn-shanghai.maxcompute.aliyun.com/api",
    )
    with o.execute_sql(
        sql, hints={"odps.sql.validate.orderby.limit": "false"}
    ).open_reader(tunnel=True) as reader:
        # type of pd_df is pandas DataFrame
        pd_df = reader.to_pandas()
    # pd_df.to_csv(f"B07DL2K5MN.csv", index=False)
    return pd_df


def phrase_similarity(text, text_list):
    doc_text = nlp(text)
    doc_target_list = [nlp(t) for t in text_list]
    score_list = np.array([doc_text.similarity(d) for d in doc_target_list])
    return text_list[score_list.argmax()]


def voc_hander(event, context):
    try:
        # logger = logging.getLogger()
        request_body = eval(event.decode("utf-8").replace("false", "False"))[0]["body"]
        logger.info(request_body)
        # logger.info(f"ALIBABA_CLOUD_ACCESS_KEY_ID={os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')}")
        sql = """
        select distinct asin,commentid, content from gmods.s_vevor_crs_crp_bazhuayu_amazon_asin_review_df 
        where ds=MAX_PT('gmods.s_vevor_crs_crp_bazhuayu_amazon_asin_review_df');
        """
        try:
            df = get_odps_data(sql)
            logger.info(f"df length:{len(df)}")
            # return str(df)
        except Exception as e:
            logger.error(e)
            return {"error": str(e)}

        df = df.dropna()
        df["token_length"] = df["content"].apply(lambda x: len(enc.encode(x)))
        llm = llm_factory["gpt4o"]
        context_length = llm_context_length["gpt4o"]

        start = 0
        context_list = []
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        while start < len(df):
            review_list = [df.iloc[start]["content"]]
            end = start + 1
            temp_tokens = df.iloc[start]["token_length"]
            while (
                end < len(df)
                and temp_tokens + df.iloc[end]["token_length"] < context_length
            ):
                review_list.append(df.iloc[end]["content"])
                temp_tokens = temp_tokens + df.iloc[end]["token_length"]
                end = end + 1
            context_list.append(
                {
                    "category": request_body["category"],
                    "reviews": "\n".join(review_list),
                }
            )
            start = end

        product_chain = voc_template | llm.with_structured_output(
            schema=Optimization_List
        )
        with get_openai_callback() as cb:
            p_list = product_chain.batch(context_list)
            total_tokens += cb.total_tokens
            prompt_tokens += cb.prompt_tokens
            completion_tokens += cb.completion_tokens

        voc_list = []
        if request_body["voc_history"]:
            for item in request_body["voc_history"]:
                voc_list.append(
                    f" - **{item['voc_key']}**: {item['voc_value']}. Number of positive reviews: {item['number_of_positive_reviews']}. Number of negative reviews: {item['number_of_negative_reviews']}."
                )
        for item in p_list:
            for opt in item.optimization_list:
                voc_list.append(
                    f" - **{opt.optimization_point}**: {opt.description}. Number of positive reviews: {opt.number_of_positive_reviews}. Number of negative reviews: {opt.number_of_negative_reviews}."
                )
        summary_chain = voc_summary_template | llm.with_structured_output(
            schema=Optimization_List
        )
        with get_openai_callback() as cb:
            p_list_2 = summary_chain.invoke({"voc_list": "\n".join(voc_list)})
            total_tokens += cb.total_tokens
            prompt_tokens += cb.prompt_tokens
            completion_tokens += cb.completion_tokens

        voc_cls_input = [
            {
                "voc_key": p.optimization_point,
                "voc_category_list": str(
                    [
                        "Product quality",
                        "Product design and function",
                        "Logistics timeliness",
                        "Service quality",
                    ]
                ),
            }
            for p in p_list_2.optimization_list
        ]
        voc_cls_chain = voc_classification_template | llm.with_structured_output(
            schema=Classification_Result
        )
        with get_openai_callback() as cb:
            cls_result_list = voc_cls_chain.batch(voc_cls_input)
            total_tokens += cb.total_tokens
            prompt_tokens += cb.prompt_tokens
            completion_tokens += cb.completion_tokens
        voc_mapping = dict(zip([p.optimization_point for  p in p_list_2.optimization_list],[c.target for c in cls_result_list]))

        logger.info(
            {
                "data": {
                    "request_id": request_body["request_id"],
                    "voc_list": [
                        {
                            "voc_key": item.optimization_point,
                            "voc_value": item.description,
                            "voc_classification":voc_mapping[item.optimization_point],
                            "number_of_positive_reviews": item.number_of_positive_reviews,
                            "number_of_negative_reviews": item.number_of_negative_reviews,
                        }
                        for item in p_list_2.optimization_list
                    ],
                },
                "status_code": 200,
                "total_tokens": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            }
        )
        return 0

        final_p_list = dict(
            [
                (
                    p.optimization_point,
                    {"description": p.description, "positive": 0, "negative": 0},
                )
                for p in p_list_2.optimization_list
            ]
        )
        final_p_list["Others"] = {"description": "Others", "positive": 0, "negative": 0}
        p_key_list = list(final_p_list.keys()) + ["Others"]

        # print(p_key_list)

        class CommentCls(BaseModel):
            point: str = Field(
                description=f"Product optimization points, must be chosen from list ({','.join(p_key_list)})"
            )
            attitude: str = Field(
                "The comment attitude, must be chosen from (positive,negative)"
            )

        attitude_chain = commentcls_template | llm.with_structured_output(
            schema=CommentCls
        )
        attitude_context_list = [
            {"reviews": _re, "optimization_point_str": ",".join(p_key_list)}
            for _re in df["content"][:]
        ]
        with get_openai_callback() as cb:
            result = attitude_chain.batch(
                attitude_context_list, config={"max_concurrency": 5}
            )
            total_tokens += cb.total_tokens
            prompt_tokens += cb.prompt_tokens
            completion_tokens += cb.completion_tokens

        # print(result)

        for atd in result:
            fix_key = phrase_similarity(atd.point, p_key_list)
            fix_attitude = phrase_similarity(atd.attitude, ["positive", "negative"])
            final_p_list[fix_key][fix_attitude] += 1

        print(
            {
                "data": {
                    "request_id": request_body["request_id"],
                    "voc_list": [
                        {
                            "voc_key": k,
                            "voc_value": v["description"],
                            "positive": v["positive"],
                            "negative": v["negative"],
                        }
                        for (k, v) in final_p_list.items()
                    ],
                },
                "status_code": 200,
                "total_tokens": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            }
        )
    except Exception as e:
        logger.error(str(e))


if __name__ == "__main__":
    bbb = [
        {
            "body": {
                "request_id": "123",
                "category": "product",
                "asin_list": ["asin1", "asin2", "asin3"],
                "voc_history": [
                    {
                        "voc_key": "Product Quality Control",
                        "voc_value": "Several reviews mentioned issues with product quality, such as broken or misaligned parts, rusting, and poor finishing. Implementing stricter quality control measures during manufacturing and packaging can help ensure that products meet the expected standards before they reach customers.",
                        "number_of_positive_reviews": 100,
                        "number_of_negative_reviews": 100,
                    }
                ],
            }
        }
    ]
    voc_hander(
        str(bbb).encode("utf-8"),
        "context",
    )
