from prometheus_client import Counter
from prometheus_fastapi_instrumentator.metrics import Info, _build_label_attribute_names
from prometheus_client import REGISTRY, CollectorRegistry, Counter, Histogram, Summary
from typing import Callable
from starlette.concurrency import iterate_in_threadpool
STATUS_COUNTER = Counter("gm_guanhai_robot_http_requests_total_500_gs", "Count of status 500", ["status_code"])
