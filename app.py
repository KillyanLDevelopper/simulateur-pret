from flask import Flask, render_template, request

app = Flask(__name__)

def calcul_amortissement(V0, taux_annuel, duree, periodicite):
    # Vérification des valeurs négatives
    if V0 <= 0 or taux_annuel < 0 or duree <= 0:
        return None, "Erreur : Le montant, la durée et le taux d'intérêt doivent être positifs."

    periodes = {"mensuel": 12, "trimestriel": 4, "semestriel": 2, "annuel": 1}
    if periodicite not in periodes:
        return None, "Périodicité invalide."

    p = periodes[periodicite]
    n = duree * p

    # Calcul correct du taux périodique
    i = (1 + (taux_annuel / 100)) ** (1 / p) - 1  

    # Formule de l'annuité constante
    A = (V0 * i) / (1 - (1 + i) ** -n)

    capital_restant = V0
    tableau = []
    total_remboursements = 0
    total_interets = 0
    total_capital_rembourse = 0

    for k in range(1, n + 1):
        interet = capital_restant * i
        capital_rembourse = A - interet
        
        # ⚠ Correction : éviter les valeurs négatives à la dernière échéance
        if capital_restant - capital_rembourse < 0:
            capital_rembourse = capital_restant  # Ajuste pour rembourser juste ce qu'il faut
            A = capital_restant + interet  # Ajuste la dernière mensualité

        capital_restant -= capital_rembourse

        tableau.append({
            "Période": k,
            "Remboursement": round(A, 2),
            "Intérêts": round(interet, 2),
            "Capital Remboursé": round(capital_rembourse, 2),
            "Capital Restant": round(capital_restant, 2)
        })

        total_remboursements += A
        total_interets += interet
        total_capital_rembourse += capital_rembourse

    totaux = {
        "Total des remboursements": round(total_remboursements, 2),
        "Total des intérêts payés": round(total_interets, 2),
        "Total du capital remboursé": round(total_capital_rembourse, 2)
    }

    return tableau, totaux

@app.route("/", methods=["GET", "POST"])
def index():
    tableau = []
    totaux = {}
    erreur = None

    if request.method == "POST":
        try:
            V0 = float(request.form["V0"])
            taux_annuel = float(request.form["taux_annuel"])
            duree = int(request.form["duree"])
            periodicite = request.form["periodicite"]

            tableau, totaux = calcul_amortissement(V0, taux_annuel, duree, periodicite)

            if tableau is None:
                erreur = totaux  # Récupère le message d'erreur
        except ValueError:
            erreur = "Erreur : Veuillez entrer des valeurs numériques valides."

    return render_template("index.html", tableau=tableau, totaux=totaux, erreur=erreur)

if __name__ == "__main__":
    app.run(debug=True)
