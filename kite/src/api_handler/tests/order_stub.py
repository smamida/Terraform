class Order:
    """
    Test stub representing an Order.
    """

    def __init__(
        self,
        order_number=None,
        kpid=None,
        coi=None,
        material_type=None,
        product=None,
        country=None,
        run_type=None,
        process_type=None,
        mfg_organization=None
    ):
        self.order_number = order_number
        self.kpid = kpid
        self.coi = coi
        self.material_type = material_type
        self.product = product
        self.country = country
        self.run_type = run_type
        self.process_type = process_type
        self.mfg_organization = mfg_organization


def existing_order():
    """
    Creates a test stub for an existing Order.
    """
    return Order(
        order_number=1,
        kpid="KPID123",
        coi="COI456",
        material_type="TypeA",
        product="ProductX",
        country="US",
        run_type="RunType1",
        process_type="ProcessType1",
        mfg_organization="Org1"
    )


def nonexistent_order():
    """
    Creates a test stub for a nonexistent (new) Order.
    """
    return Order(
        order_number=2,
        kpid="KPID789",
        coi="COI012",
        material_type="TypeB",
        product="ProductY",
        country="UK",
        run_type="RunType2",
        process_type="ProcessType2",
        mfg_organization="Org2"
    )


def unknown_order():
    """
    Creates a test stub for an unknown Order.
    """
    return Order(
        order_number=999,
        kpid="UNKNOWN",
        coi="UNKNOWN",
        material_type="Unknown",
        product="Unknown",
        country="XX",
        run_type="Unknown",
        process_type="Unknown",
        mfg_organization="Unknown"
    )
