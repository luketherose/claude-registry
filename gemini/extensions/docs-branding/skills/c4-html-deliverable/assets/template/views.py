"""Views of the C4 model: node positions are centres (cx, cy, width) on the canvas `size`."""
from model import R

L1 = dict(
    id="l1", level="Level 1", kind="System Context", nav="System Context",
    title="System Context diagram for the Order Management Platform",
    scope="The platform, the people who use it and the systems it depends on.",
    size=(1300, 1000),
    nodes={
        "p_agent": (400, 160, 230), "p_admin": (860, 160, 230),
        "x_idp": (170, 540, 230), "s_oms": (630, 540, 320), "x_pay": (1110, 540, 230),
        "x_erp": (630, 890, 230),
    },
    zones=[
        dict(id="z_users", label="Corporate network", members=["p_agent", "p_admin"], pad=24),
    ],
    edges=[
        R("p_agent", "s_oms", "Places and amends orders", "HTTPS", t=0.5, wc=18),
        R("p_admin", "s_oms", "Manages rules and users", "HTTPS", t=0.5, wc=18),
        R("s_oms", "x_idp", "Signs users in", "OIDC", t=0.5, dy=-30, wc=16),
        R("s_oms", "x_pay", "Authorises and captures payments", "REST/HTTPS", shift=-14, t=0.5, dy=-34, wc=18),
        R("x_pay", "s_oms", "Notifies payment outcomes", "Webhook, HTTPS", shift=-14, t=0.5, dy=34, wc=18),
        R("s_oms", "x_erp", "Sends paid orders", "REST/HTTPS", t=0.5, wc=16),
    ],
    notes=[
        "The payment provider is a SaaS on the internet; card data never enters the platform.",
    ],
)

L2 = dict(
    id="l2", level="Level 2", kind="Container", nav="Containers",
    title="Container diagram for the Order Management Platform",
    scope="The web app, two backend containers and two data stores, grouped by where they run.",
    size=(1880, 960),
    nodes={
        "x_idp": (620, 110, 240), "x_pay": (1180, 110, 240),
        "p_agent": (150, 430, 220), "p_admin": (150, 730, 220),
        "c_web": (520, 430, 250), "c_api": (900, 430, 250), "c_worker": (1280, 430, 250),
        "c_db": (710, 790, 250), "c_topic": (1090, 790, 250),
        "x_erp": (1700, 430, 240),
    },
    flow_layout=dict(
        size=(1340, 700),
        nodes={
            "x_idp": (450, 90, 200), "x_pay": (850, 90, 200),
            "p_agent": (100, 330, 160), "p_admin": (100, 540, 160),
            "c_web": (380, 330, 200), "c_api": (660, 330, 200), "c_worker": (940, 330, 200),
            "c_db": (520, 570, 200), "c_topic": (800, 570, 200),
            "x_erp": (1220, 330, 200),
        },
    ),
    zones=[
        dict(id="z_id", label="Corporate identity", members=["x_idp"], pad=22),
        dict(id="z_pay", label="Internet", members=["x_pay"], pad=22),
        dict(id="z_users", label="Corporate network", members=["p_agent", "p_admin"], pad=22),
        dict(id="z_k8s", label="Kubernetes cluster", members=["c_web", "c_api", "c_worker"], pad=28),
        dict(id="z_data", label="Managed data services", members=["c_db", "c_topic"], pad=28),
        dict(id="z_sys", kind="system", eid="s_oms", label="Order Management Platform",
             sub="[Software System] in the corporate cloud", members=["z_k8s", "z_data"], pad=26, anchor="right"),
        dict(id="z_erp", label="Corporate data centre", members=["x_erp"], pad=22),
    ],
    edges=[
        R("p_agent", "c_web", "Places and amends orders", "HTTPS", t=0.5, wc=16),
        R("p_admin", "c_web", "Manages rules and users", "HTTPS", t=0.45, wc=16),
        R("c_web", "x_idp", "Signs the user in", "OIDC", t=0.5, wc=14),
        R("c_web", "c_api", "Calls the API with the user token", "JSON/HTTPS", t=0.5, wc=16),
        R("c_api", "x_idp", "Fetches token signing keys", "OIDC JWKS", t=0.5, wc=14),
        R("c_api", "x_pay", "Authorises and captures payments", "REST/HTTPS", shift=-14, t=0.3, wc=16),
        R("x_pay", "c_api", "Notifies payment outcomes", "Webhook, HTTPS", shift=-14, t=0.3, wc=16),
        R("c_api", "c_db", "Reads and writes orders and the outbox", "JDBC", t=0.5, wc=16),
        R("c_api", "c_topic", "Publishes order events", "Kafka", style="async", t=0.5, wc=14),
        R("c_topic", "c_worker", "Delivers paid orders", "Kafka", style="async", t=0.5, wc=14),
        R("c_worker", "c_db", "Records the fulfilment outcome", "JDBC", t=0.3, wc=16),
        R("c_worker", "x_erp", "Sends paid orders", "REST/HTTPS", t=0.5, wc=12, assumption=True),
    ],
    notes=[
        "The order and its event are written in one transaction (outbox); the event reaches the topic at least once.",
        "Zones show where each element runs; network details belong to the deployment view.",
    ],
)

# The use cases, drawn as tabs on the compact layout of L2.
L2["flows"] = [
    dict(
        id="uc1", short="Place an order", title="Use case 1: Place an order",
        lead="A service agent places an order for a customer and the payment is authorised.",
        hi=["p_agent", "c_web", "x_idp", "c_api", "x_pay", "c_db", "c_topic"],
        steps=[
            dict(text="The agent opens the web app and signs in.", calls=["p_agent>c_web", "c_web>x_idp"]),
            dict(text="The web app sends the order to the Order API with the user token.", calls=["c_web>c_api", "c_api>x_idp"]),
            dict(text="The Order API authorises the payment.", calls=["c_api>x_pay"]),
            dict(text="It writes the order and its event in one transaction.", calls=["c_api>c_db"]),
            dict(text="The event is published on the order topic.", calls=["c_api>c_topic"]),
        ],
    ),
    dict(
        id="uc2", short="Fulfil a paid order", title="Use case 2: Fulfil a paid order",
        lead="Each paid order reaches the ERP with nobody touching it.",
        hi=["c_topic", "c_worker", "x_erp", "c_db"],
        steps=[
            dict(text="The topic delivers the paid order to the fulfilment worker.", calls=["c_topic>c_worker"]),
            dict(text="The worker sends the order to the ERP.", calls=["c_worker>x_erp"]),
            dict(text="The ERP ships and invoices the order.", calls=["@x_erp"]),
            dict(text="The worker records the outcome on the order.", calls=["c_worker>c_db"]),
        ],
    ),
]

L3_API = dict(
    id="l3-api", level="Level 3", kind="Component", nav="Order API",
    title="Component diagram for the Order API",
    scope="How an order call becomes a payment, a row and an event.",
    size=(1800, 1140),
    boundary=dict(eid="c_api", members=["k_ctrl", "k_svc", "k_pay", "k_repo", "k_pub"]),
    nodes={
        "c_web": (130, 380, 220),
        "k_ctrl": (480, 380, 230), "k_svc": (860, 380, 230), "k_pay": (1240, 380, 230),
        "x_pay": (1640, 380, 230),
        "k_pub": (480, 700, 230), "k_repo": (860, 700, 230),
        "c_topic": (480, 1050, 230), "c_db": (860, 1050, 250),
    },
    edges=[
        R("c_web", "k_ctrl", "Sends order calls", "JSON/HTTPS", t=0.5, wc=12),
        R("k_ctrl", "k_svc", "Delegates", t=0.5, wc=12),
        R("k_svc", "k_pay", "Charges the payment", t=0.5, wc=12),
        R("k_pay", "x_pay", "Authorises and captures", "REST/HTTPS", t=0.5, wc=12),
        R("k_svc", "k_repo", "Writes order and outbox", t=0.5, wc=14),
        R("k_pub", "k_repo", "Reads pending events", t=0.5, wc=12),
        R("k_pub", "c_topic", "Publishes events", "Kafka", style="async", t=0.5, wc=12),
        R("k_repo", "c_db", "Reads and writes", "JDBC", t=0.5, wc=12),
    ],
    notes=[
        "The controller holds no rule; validation and the payment call live in the order service.",
    ],
)

VIEWS = [L1, L2, L3_API]
