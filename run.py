from PrizeBondApp import create_app
from PrizeBondApp.utils import UtilityFunctions
from PrizeBondApp.models import *
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
            "db": db, "User": User, "BondPrice": BondPrice, "userbond": userbond,
            "BondPrize": BondPrize, "Bond": Bond, "WinningBond": WinningBond, "DrawDate": DrawDate,
            "DrawLocation": DrawLocation, "DrawNumber": DrawNumber, "Role": Role, "UpdatedLists": UpdatedLists,
            "Notifications": Notifications
           }
app.jinja_env.globals['UtilityFunctions'] = UtilityFunctions
app.jinja_env.globals['len'] = len
app.jinja_env.globals['str'] = str

if __name__ == "__main__":
    app.run(debug=False)