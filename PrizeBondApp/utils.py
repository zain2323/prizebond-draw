from PrizeBondApp.models import BondPrice, BondPrize, DrawDate
from pathlib import Path
import secrets

class UtilityFunctions:

    @staticmethod
    def load_denominations():
        denominations = BondPrice.query.all()
        return [d.price for d in denominations]
    
    @staticmethod
    def load_date(denomination):
        try:
            denomination = int(denomination)
        except:
            return []
        bond_price = BondPrice.query.filter_by(price=denomination).first()
        date = DrawDate.query.filter_by(price=bond_price).all()
        return [str(d.date) for d in date]
    
    @staticmethod
    def load_prizes():
        prizes = BondPrize.query.all()
        return [d.prize for d in prizes]
    
    @staticmethod
    def load_user_bonds(user):
        bonds = user.get_bonds()
        return [bond.serial for bond in bonds]

    @staticmethod
    def load_denomination_prizes(price):
        denominations = BondPrice.query.filter_by(price=price).first()
        bond_prizes = BondPrize.query.filter_by(bond_price_id=denominations.id).all()
        return [bond_prize.prize for bond_prize in bond_prizes]
    
    @staticmethod
    def save_picture(file_data):
        '''
        This saves the thumbnail picture of the product in the static/product_pictures directory.
        Picture is being renamed  to the randomly chosen 32 bit string in order to avoid the
        naming clash.
        '''
        try:
            path = Path('./PrizeBondApp/static/results')
        except FileNotFoundError:
            raise FileNotFoundError("Path is invalid or does not exist.")
        try:
            _, ext = file_data.filename.split(".")
        except:
            ext = file_data.filename.split(".")[-1]
        file_name_with_ext = UtilityFunctions.generate_hex_name() + "." + ext
        path = path.joinpath(file_name_with_ext)
        file_data.save(path)
        return file_name_with_ext
    
    @staticmethod
    def delete_picture(img_name):
        try:
            path = Path("./PrizeBondApp/static/results/" + img_name)
        except FileNotFoundError:
            raise FileNotFoundError("Path is invalid or does not exist.")
        if path.exists():
            path.unlink()
        else:
            raise FileNotFoundError("File with the given name do not exists.")
    
    @staticmethod
    def generate_hex_name():
        '''
        Returns the 32 bit random digits
        '''
        return secrets.token_hex(32)

    @staticmethod
    def normalize_serials(serials):
        serials = serials.split(",")
        serials = list(map(str.strip, serials))
        while("" in serials):
            serials.remove("")
        return serials

    @staticmethod
    def count_leading_zeroes(serial):
        count = 0
        for char in serial: 
            if char != '0':
                break
            count += 1
        return count
    
    @staticmethod
    def append_leading_zeroes(serial_start, serial_end):
        diff = abs(len(serial_start) - len(serial_end))
        zeroes = ""
        for i in range(diff):
            zeroes += '0'
        return zeroes + serial_end
