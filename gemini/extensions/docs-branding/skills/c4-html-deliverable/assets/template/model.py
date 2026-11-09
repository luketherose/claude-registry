"""C4 model of the project: every element once, with its type, technology and responsibility.

This is the worked example shipped with the skill (a fictional order platform). Copy the
three files of this folder into the project, then replace the elements, keeping the ids short.
"""

ELEMENTS = {
    # People
    "p_agent": dict(kind="person", name="Service agents",
                    desc="Place and amend orders on behalf of customers"),
    "p_admin": dict(kind="person", name="Platform administrators",
                    desc="Manage catalogue rules, users and integrations"),

    # Software systems
    "s_oms": dict(kind="system", name="Order Management Platform",
                  desc="Takes orders, charges the payment and sends paid orders to fulfilment"),
    "x_idp": dict(kind="system_ext", name="Corporate identity provider",
                  desc="Single sign-on; issues OIDC tokens"),
    "x_pay": dict(kind="system_ext", name="Payment provider",
                  desc="Authorises and captures card payments"),
    "x_erp": dict(kind="system_ext", name="ERP",
                  desc="Warehouse and invoicing: ships and bills the order"),

    # Containers
    "c_web": dict(kind="spa", name="Web app", tech="React, TypeScript",
                  desc="Order entry and back office screens"),
    "c_api": dict(kind="container", name="Order API", tech="Java 21, Spring Boot 3",
                  desc="Orders, payments and customers; the only backend entry of the web app"),
    "c_worker": dict(kind="container", name="Fulfilment worker", tech="Java 21, Spring Boot 3",
                     desc="Sends paid orders to the ERP and records the outcome"),
    "c_db": dict(kind="db", name="Order database", tech="PostgreSQL",
                 desc="Orders, payments, customers and the outbox"),
    "c_topic": dict(kind="db", name="Order events topic", tech="Kafka topic",
                    desc="One event per paid order"),

    # Components of the Order API
    "k_ctrl": dict(kind="component", name="Order controller", tech="Spring MVC controller",
                   desc="/orders: create, amend, cancel, read"),
    "k_svc": dict(kind="component", name="Order service", tech="Spring service",
                  desc="Validates the order, charges the payment, writes order and outbox in one transaction"),
    "k_pay": dict(kind="component", name="Payment client", tech="REST client",
                  desc="Authorises and captures through the payment provider"),
    "k_repo": dict(kind="component", name="Repository", tech="Spring Data JPA",
                   desc="Orders, payments and outbox"),
    "k_pub": dict(kind="component", name="Outbox publisher", tech="Scheduled job",
                  desc="Publishes pending events to the topic, at least once"),
}


def R(src, dst, label, tech="", style="sync", via=None, t=0.5, dx=0, dy=0, shift=0, assumption=False, wc=30,
      key=None, bt=None):
    """A relationship.

    style: "sync" or "async". via: waypoints. t: where the label sits along the path (0 to 1),
    moved by dx and dy. shift: parallel offset for two arrows between the same pair. wc: label
    wrap width in characters. key: name used by the use-case steps (default "src>dst").
    bt: where the step badge sits along the path, when it must differ from t.
    """
    return dict(src=src, dst=dst, label=label, tech=tech, style=style, via=via or [], t=t,
                dx=dx, dy=dy, shift=shift, assumption=assumption, wc=wc,
                key=key or f"{src}>{dst}", bt=bt)
