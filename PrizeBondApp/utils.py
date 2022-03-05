from PrizeBondApp.models import BondPrice, BondPrize, DrawDate
from pathlib import Path
import secrets

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
from flask import render_template, current_app as app

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
    
    @staticmethod
    def extract_continuous_characters(text):
        for i in range(len(text)):
            if text[i:].isnumeric() and len(text[i:]) == 6:
                return text[i:]
        return None
    
    @staticmethod
    def extract_serial_from_img(filename):
        serial = None
        denomination = None
        subscription_key = app.config["SUBSCRIPTION_KEY"]
        endpoint = app.config["ENDPOINT"]
        computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
        read_response = computervision_client.read_in_stream(filename, raw=True)
        read_operation_location = read_response.headers["Operation-Location"]
        operation_id = read_operation_location.split("/")[-1]
        # Call the "GET" API and wait for the retrieval of the results
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status.lower () not in ['notstarted', 'running']:
                break
            time.sleep(10)
        # Print results, line by line
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    if line.text in ["200", "750", "100", "1500"]:
                        denomination = line.text
                    if serial is None:
                        serial = UtilityFunctions.extract_continuous_characters(line.text)
        return serial, denomination
