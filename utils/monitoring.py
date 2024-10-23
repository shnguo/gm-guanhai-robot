from prometheus_client import Counter
from prometheus_fastapi_instrumentator.metrics import Info, _build_label_attribute_names
from prometheus_client import REGISTRY, CollectorRegistry, Counter, Histogram, Summary
from typing import Callable
from starlette.concurrency import iterate_in_threadpool
STATUS_COUNTER = Counter("gm_guanhai_robot_http_requests_total_500_gs", "Count of status 500", ["status_code"])
# import sentry_sdk

# sentry_sdk.init(
#     dsn="https://d749964ece03ab1c418913ac5d1e9e54@o4508141398261760.ingest.us.sentry.io/4508141400031232",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for tracing.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )
