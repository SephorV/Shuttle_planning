import pandas as pd

# ============================================================
# RELATIONSHIP TABLE (HARDCODED)
# ============================================================

def get_relationship_table():

    data = [
        ["S400 HEV Excellence","KU","S400 HEV-Excellence-Moonlight Silver"],
        ["S400 HEV Excellence","GV","S400 HEV-Excellence-Grey"],
        ["S400 HEV Excellence","CL","S400 HEV-Excellence-Black"],
        ["S400 HEV Excellence","BW","S400 HEV-Excellence-White"],
        ["S400 HEV Excellence","NL","S400 HEV-Excellence-Red"],

        ["S400 HEV Premium","GV","S400 HEV-Premium-Grey"],
        ["S400 HEV Premium","BW","S400 HEV-Premium-White"],
        ["S400 HEV Premium","CL","S400 HEV-Premium-Black"],
        ["S400 HEV Premium","KU","S400 HEV- Premium - Moonlight Silver"],
        ["S400 HEV Premium","NL","S400 HEV-Premium-Red"],

        ["S700 Comfort","GV","S700-Comfort-Grey"],
        ["S700 Comfort","CL","S700-Comfort-Black"],
        ["S700 Comfort","BW","S700-Comfort-White"],

        ["S700 HEV Luxury","BW","S700 HEV - Luxury - Blanco Khaki"],
        ["S700 HEV Luxury","CL","s700 HEV - Luxury - Negro Carbono"],
        ["S700 HEV Luxury","ZE","s700 HEV - Luxury - Bitono Blanco Negro"],
        ["S700 HEV Luxury","GV","s700 HEV - Luxury - Gris Phantom"],
        ["S700 HEV Luxury","ZF","s700 HEV - Luxury - Bitono Rojo Negro"],

        ["S700 Luxury","GV","S700-Luxury-Grey"],
        ["S700 Luxury","ZE","S700-Luxury-Bitone Black & White"],
        ["S700 Luxury","CL","S700-Luxury-Black"],
        ["S700 Luxury","BW","S700-Luxury-White"],

        ["S700 PHEV Luxury","BW","S700 PHEV-Luxury-White"],
        ["S700 PHEV Luxury","CL","S700 PHEV-Luxury-Black"],
        ["S700 PHEV Luxury","GV","S700 PHEV-Luxury-Grey"],
        ["S700 PHEV Luxury","ZE","S700 PHEV-Luxury-Bition"],
        ["S700 PHEV Luxury","ZF","S700 PHEV-Luxury-Bitone Red"],

        ["S700 PHEV Premium","ZE","S700 PHEV-Premium-Bitone"],
        ["S700 PHEV Premium","GV","S700 PHEV-Premium-Grey"],
        ["S700 PHEV Premium","CL","S700 PHEV-Premium-Black"],
        ["S700 PHEV Premium","BW","S700 PHEV-Premium-White"],
        ["S700 PHEV Premium","ZF","S700 PHEV-Premium-Bitone Red"],

        ["S800 Luxury","BW","S800-Luxury-White"],
        ["S800 Luxury","SJ","S800-Luxury-Green Aurora"],
        ["S800 Luxury","CL","S800-Luxury-Black"],
        ["S800 Luxury","UM","S800-Luxury-Grey Bamboo"],

        ["S800 PHEV Luxury","UM","S800 PHEV-Luxury-Grey Bamboo"],
        ["S800 PHEV Luxury","UV","S800 PHEV-Luxury-Gris Eclipse Matt"],
        ["S800 PHEV Luxury","SJ","S800 PHEV-Luxury-Green Aurora"],
        ["S800 PHEV Luxury","BW","S800 PHEV-Luxury-White"],
        ["S800 PHEV Luxury","CL","S800 PHEV-Luxury-Black"],

        ["S800 PHEV Premium","UM","S800 PHEV-Premium-Grey"],
        ["S800 PHEV Premium","SJ","S800 PHEV-Premium-Green Aurora"],
        ["S800 PHEV Premium","BW","S800 PHEV-Premium-White"],
        ["S800 PHEV Premium","CL","S800 PHEV-Premium-Black"],

        ["S800 Premium","UM","S800-Premium-Grey Bamboo"],
        ["S800 Premium","CL","S800-Premium-Black"],
        ["S800 Premium","SJ","S800-Premium-Green Aurora"],
        ["S800 Premium","BW","S800-Premium-White"],

        ["S900 PHEV Luxury","CM","S900 PHEV - Luxury - Black Ink"],
        ["S900 PHEV Luxury","GX","S900 PHEV - Luxury - Tech Grey"],
        ["S900 PHEV Luxury","UE","S900 PHEV - Luxury - Matt Grey"],
        ["S900 PHEV Luxury","SJ","S900 PHEV - Luxury - Aurora Green"],
        ["S900 PHEV Luxury","BX","S900 PHEV - Luxury - Snow White"],
    ]

    rel = pd.DataFrame(data, columns=["model_trim","color_code","product"])
    rel["vehicle_key"] = rel["model_trim"] + " | " + rel["color_code"]
    return rel

# ============================================================
# CONFIGURAÇÃO DAS CAMPAS
# ============================================================

def get_compounds():
    return pd.DataFrame([
        {"code":"B0003","compound":"Barcelona_TRADISA","capacity":1000,"used":0,"logistic":"Tradisa"},
        {"code":"B0004","compound":"Barcelona_SETRAM_PARK","capacity":1200,"used":600,"logistic":"Setram"},
        {"code":"B0005","compound":"Barcelona_CALAF","capacity":1500,"used":0,"logistic":"Autoflotas"},
        {"code":"M0002","compound":"Madrid_SEMAT","capacity":850,"used":0,"logistic":"CEVA"},
    ])

# ============================================================
# STOCK ATUAL DO DATAVERSE
# ============================================================

def get_current_stock(df):
    stock = df[
        (df["new_preallotstatus"].astype(str).isin(["10","20"])) &
        (df["new_status"].astype(str).isin(["12","20","80"]))
    ].copy()
    return (
        stock.groupby(["new_ebrowarehouse_idname","new_product_idname"])
        .size().reset_index(name="qty")
    )

# ============================================================
# CÁLCULO DE CAPACIDADE
# ============================================================

def compute_compound_status(stock_df, compounds_df):
    total_stock = (
        stock_df.groupby("new_ebrowarehouse_idname")["qty"]
        .sum()
        .reset_index()
        .rename(columns={"new_ebrowarehouse_idname":"compound"})
    )
    compounds = compounds_df.merge(total_stock, how="left", on="compound")
    compounds["qty"] = compounds["qty"].fillna(0) + compounds["used"].fillna(0)
    compounds["free_capacity"] = compounds["capacity"] - compounds["qty"]

    operational_table = compounds.copy()

    total_row = pd.DataFrame([{
        "code":"TOTAL", "compound":"TOTAL",
        "capacity": compounds["capacity"].sum(),
        "used": compounds["used"].sum(),
        "qty": compounds["qty"].sum(),
        "free_capacity": compounds["free_capacity"].sum(),
        "logistic":""
    }])
    reporting_table = pd.concat([compounds, total_row], ignore_index=True)
    return operational_table, reporting_table

# ============================================================
# INBOUND → PRODUCT
# ============================================================

def get_inbound_ready(inbound_df):
    rel = get_relationship_table()
    inbound_df["vehicle_key"] = inbound_df["Model and Trim"] + " | " + inbound_df["Color Code"]
    inbound = inbound_df.merge(rel, how="left", on="vehicle_key")

    if inbound["product"].isna().any():
        missing = inbound[inbound["product"].isna()]["vehicle_key"].unique()
        raise Exception(f"Missing mapping: {missing}")

    inbound = inbound.rename(columns={"VIN":"vin"})
    return inbound[["vin","product"]]

# ============================================================
# MOTOR DE DECISÃO COM BALANCEAMENTO LOGÍSTICO
# ============================================================

def choose_best_compound(
    product, stock_by_model, compounds_status,
    logistic_counts, logistic_weight=0.3
):
    """
    product: nome do produto
    stock_by_model: DataFrame com ['new_ebrowarehouse_idname','new_product_idname','qty']
    compounds_status: DataFrame operacional das campas (sem linha TOTAL)
    logistic_counts: dict {compound: total atribuído durante este ciclo}
    logistic_weight: peso do balanceamento logístico (0 = ignora, 1 = muito forte)
    """

    # Capacidade total do sistema para calcular a quota ideal de cada transportista
    total_capacity = compounds_status["capacity"].sum()
    # Número total de carros atribuídos até agora (para calcular a share real)
    total_assigned = sum(logistic_counts.values())

    scores = []
    for _, c in compounds_status.iterrows():
        if c.free_capacity <= 0:
            continue

        compound = c.compound
        logistic = c.logistic

        # 1) Carga relativa do parque
        compound_total = stock_by_model[
            stock_by_model["new_ebrowarehouse_idname"] == compound
        ]["qty"].sum()
        load_ratio = compound_total / c.capacity

        # 2) Mix do modelo específico no parque
        model_stock = stock_by_model[
            (stock_by_model["new_ebrowarehouse_idname"] == compound) &
            (stock_by_model["new_product_idname"] == product)
        ]["qty"].sum()
        model_ratio = model_stock / (compound_total + 1)

        # 3) Capacidade livre
        free_ratio = c.free_capacity / c.capacity

        # 4) Balanceamento logístico
        # Quota ideal de cada transportista = soma das capacidades dos seus parques / capacidade total
        logistic_capacity = compounds_status[compounds_status.logistic == logistic]["capacity"].sum()
        target_share = logistic_capacity / total_capacity

        # Share atual do transportista entre os carros já atribuídos
        current_logistic_assigned = sum(
            logistic_counts[comp]
            for comp in compounds_status[compounds_status.logistic == logistic].compound
        )
        actual_share = current_logistic_assigned / (total_assigned + 1)  # +1 evita divisão por zero

        # Quanto mais próximo da target melhor
        logistic_score = 1 - abs(target_share - actual_share)

        # Score final: três primeiros componentes têm pesos fixos, o logístico é ponderado pelo slider
        score = (
            (1 - load_ratio) * 0.5 +
            (1 - model_ratio) * 0.3 +
            free_ratio * 0.2
        ) * (1 - logistic_weight) + logistic_score * logistic_weight

        scores.append((compound, score))

    if not scores:
        return None

    return sorted(scores, key=lambda x: x[1], reverse=True)[0][0]


def plan_shuttle(inbound_df, stock_by_model, compounds_status, logistic_weight=0.3):
    plans = []
    # Dicionário que guarda quantos carros já foram atribuídos a cada compound (neste ciclo)
    logistic_counts = {c: 0 for c in compounds_status.compound}

    for _, car in inbound_df.iterrows():
        product = car["product"]
        vin = car["vin"]

        best = choose_best_compound(
            product, stock_by_model, compounds_status,
            logistic_counts, logistic_weight
        )
        if best is None:
            continue

        # Atualizar stock virtual
        mask = (
            (stock_by_model["new_ebrowarehouse_idname"] == best) &
            (stock_by_model["new_product_idname"] == product)
        )
        if mask.any():
            stock_by_model.loc[mask, "qty"] += 1
        else:
            stock_by_model.loc[len(stock_by_model)] = [best, product, 1]

        # Atualizar capacidade livre do compound
        compounds_status.loc[
            compounds_status.compound == best, "free_capacity"
        ] -= 1

        # Contagem logística
        logistic_counts[best] += 1

        row = compounds_status[compounds_status.compound == best].iloc[0]
        plans.append([
            vin, "", "", "B0001", "Barcelona_EBRO",
            product, row.code, best, "", row.logistic
        ])

    columns = [
        "VIN","Parking List No","Product Code (Product) (Product)",
        "Code (Departure From) (Ebro Warehouse)","Departure From",
        "Product","Code (Arrive Site) (Ebro Warehouse)","Arrive Site",
        "Description (Arrive Site) (Ebro Warehouse)","Logistic Company"
    ]
    return pd.DataFrame(plans, columns=columns)


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def run_engine(dataverse_df, inbound_df, compounds_df, logistic_weight=0.3):
    stock = get_current_stock(dataverse_df)
    compounds_operational, compounds_reporting = compute_compound_status(stock, compounds_df)
    inbound_ready = get_inbound_ready(inbound_df)

    shuttle_plan = plan_shuttle(
        inbound_ready, stock, compounds_operational, logistic_weight
    )
    return shuttle_plan, compounds_reporting, stock