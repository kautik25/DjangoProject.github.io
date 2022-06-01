import requests
import random
from ccavutil import encrypt,decrypt
import os
from django.conf import settings
import xml.etree.ElementTree as ET

biller_info_req_url = 'https://stgapi.billavenue.com/billpay/extMdmCntrl/mdmRequestNew/xml'
bill_payment_req_url = "https://stgapi.billavenue.com/billpay/extBillPayCntrl/billPayRequest/xml"
transaction_status_req_url = "https://stgapi.billavenue.com/billpay/transactionStatus/fetchInfo/xml"
deposite_enquiry_req_url = "https://stgapi.billavenue.com/billpay/enquireDeposit/fetchDetails/xml"

accessCode = "AVQW44CY59KI48PVMS"

#access code for http://paybills.today
#accessCode = "AVAN75FA46AS98NASA"
ver = "1.0",
instituteId = "KD12"
working_key	= b"FC98690B8615B5A1D1C461E4091B9A3D"

billerID_dict = {
    "AIRTEL" : "BILAVAIRTEL001",
	"Jio" : "BILAVJIO000001",
	"MTNL_Mumbai" : "BILAVMTNL00001",
	"MTNL_Delhi" : "BILAVMTNL00002",
	"VI" : "BILAVVI0000001",
}

def generateRandomString(length):
    characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    charactersLength = len(characters)
    randomString = ''

    for i in range(0, length):
        randomString = randomString + characters[random.randint(0, charactersLength - 1)]
    return randomString

def bill_avenue_biller_info_req(req_url, xml_req):
    try:
        encRequestXML = encrypt(xml_req, working_key)
        requestId = generateRandomString(35)
        print("\n\nrequestId:", requestId)
        params = {
            "accessCode":accessCode, 
            "requestId": requestId,
            "ver" : ver,
            "instituteId": instituteId,
        }

        response = requests.post(req_url, params=params, data=encRequestXML)
        print("\n\nResponse.status_code",response.status_code)
        print("\n\nresponse.content", response.content)

        if response.status_code == 200:
            decryptedText = decrypt(response.content, working_key)
            return decryptedText
        return "Response status is not 200"

    except Exception as e:
        print("errorMsg",str(e))
        return str(e)

def bill_avenue_req(req_url, xml_req):
    try:
        encRequestXML = encrypt(xml_req, working_key)
        requestId = generateRandomString(35)
        print("\n\nrequestId:", requestId)

        data = {
            "accessCode":accessCode, 
            "requestId": requestId,
            "ver" : ver,
            "instituteId": instituteId,
            "encRequest" : encRequestXML,
        }
        response = requests.post(req_url, data=data)
        print("\n\nResponse.status_code",response.status_code)
        print("\n\nresponse.content", response.content)

        if response.status_code == 200:
            decryptedText = decrypt(response.content, working_key)
            return decryptedText
        return "Response status is not 200"

    except Exception as e:
        print("errorMsg",str(e))
        return str(e)

def ccavenue_payment_req():
    try:
        req_url = "https://test.ccavenue.com/transaction/transaction.do?command=initiateTransaction"
        encReq = b'fbe47923feb219eb0b7f30e2474f64ce03288d99b036bc1aa54a20b89ed5443e90d916e63605127b6797b9179d1d7c2b5078bea8a8e81611d8bd73be5fa1a0923daea462960b37c403cf7288c9eb5d682da239a330f0d6a3ce296a7489fbf96d9e6fe957275c453ee39999c0b8d522ca5e1e16599a0c868de90b6513290ce191e596748edd977023cb9aae7983868699ba056284a4cf15028ac6406a664a87931461f56c906ae26faca0867522ff0fdfb715612df5b444ac5d01494912b8fda68db4a3fbd143456398673a0825f143cad47e5e7d3b69ca3a30dfc29b252bc226f2db28db61ff41392a1343b59e8d53ff18579646b9e1bb99d50838902cea8b263d46b9ce496e85ae02b1db6705265006f687e3314716222de109d9725efcc8f6707845130dae39149307fec10202f1cb883ea103d4e19ee34bd12b0cfe2245c06db2a81b3452f7b9307685afb2ae026a55496ed112a33a1b12351e07bc17152af9c1cbbcfb31f02bf88c2536cd6567c9afa6dbc08f57df086d08456d816b1ed3dd01fa9a42a989aa22300551c5aa7d1f384fb1bd566369d2d82beebb73c534f8c2114e06415235c49b45d835c36faa29e54dddd100a9c3ddf0d8e7eb43f4c9a2b693d23c5ce8dc75bda5347fe2d4f56269e98375cb54c563d47a62221df279df08f607d659b5cdc053cf347f45cb7e8adc577915940d2e20ae40c595c4fbbfd7a94fb1a8f8d4fbb8cc055738b52e30e1507025991c4eeeb35c85821492e3d5d590f6f923b94342fd666b69251834cee4fea4c2c667e4fe1a877b612b21e2daa14ec4edaea6916c1db37f17d93a9c73b4c8da9dfff8e47284435c0e8deeb149d0486a500a639e153c02279f49eafa0e5d85d4cf72aa72567b89ad8b632fc3841b38ce40f50f43dbd3af75d5fa43d5196c0eb9d440bc68414eac78fa97e2fe95803790406b778d600436f092e2299f5a6282d5f38e52523340635e518ab5d12e78aa946a59935fc1913dab23e4a69142d2'
        data = {
            "encReq":encReq,
            "accessCode":accessCode, 
        }

        response = requests.post(req_url, data=data)
        print("\n\nResponse.status_code",response.status_code)
        print("\n\nresponse.content", response.content)

        if response.status_code == 200:
            decryptedText = decrypt(response.content, working_key)
            return decryptedText
        return "Response status is not 200"

    except Exception as e:
        print("errorMsg",str(e))
        return str(e)

biller_info_xml_request = '<?xml version="1.0" encoding="UTF-8"?><billerInfoRequest><billerId>%s</billerId></billerInfoRequest>'%(billerID_dict['AIRTEL'])
bill_payment_xml_request = '<?xml version="1.0" encoding="UTF-8"?><billPaymentRequest><agentId>CC01CC01513515340681</agentId><billerAdhoc>true</billerAdhoc><agentDeviceInfo><ip>134.209.116.97</ip><initChannel>AGT</initChannel><mac>e6:3c:89:33:18:1e</mac></agentDeviceInfo><customerInfo><customerMobile>9876543210</customerMobile><customerEmail></customerEmail><customerAdhaar></customerAdhaar><customerPan></customerPan></customerInfo><billerId>BILAVAIRTEL001</billerId><inputParams><input><paramName>Location</paramName><paramValue>Mumbai</paramValue></input><input><paramName>Mobile Number</paramName><paramValue>9898981000</paramValue></input></inputParams><amountInfo><amount>100000</amount><currency>356</currency><custConvFee>0</custConvFee><amountTags></amountTags></amountInfo><paymentMethod><paymentMode>Cash</paymentMode><quickPay>Y</quickPay><splitPay>N</splitPay></paymentMethod><paymentInfo><info><infoName>Remarks</infoName><infoValue>Received</infoValue></info></paymentInfo></billPaymentRequest>'
# transaction_status_xml_request = '<?xml version="1.0" encoding="UTF-8"?><transactionStatusReq><trackType>TRANS_REF_ID</trackType><trackValue>CC0175192009</trackValue></transactionStatusReq>'
deposite_enquiry_xml_request = '<?xml version="1.0" encoding="UTF-8"?><depositDetailsRequest><fromDate>2021-09-01</fromDate><toDate>2021-09-17</toDate><transType>DR</transType><agents><agentId>CC01CC01513515340681</agentId></agents></depositDetailsRequest>'
transaction_status_xml_request = '<?xml version="1.0" encoding="UTF-8"?><transactionStatusReq><trackType>TRANS_REF_ID</trackType><trackValue>CC011280BAAC00051187</trackValue></transactionStatusReq>'

if __name__ == "__main__":
    response = bill_avenue_biller_info_req(biller_info_req_url, biller_info_xml_request)
    print("biller info response:",response)

    # with open('data.xml', 'w') as f:
    #     f.write(response)
    #     f.close()
    #     print("Written response in XML file")       

    print("bill_payment_req_url", bill_payment_req_url)
    print("\n\nbill_payment_xml_request", bill_payment_xml_request)
    response = bill_avenue_req(bill_payment_req_url, bill_payment_xml_request)
    print("Bill payment response:",response)

    print("\n\ndeposite_enquiry_req_url", deposite_enquiry_req_url)
    print("\n\ndeposite_enquiry_xml_request", deposite_enquiry_xml_request)
    response = bill_avenue_req(deposite_enquiry_req_url, deposite_enquiry_xml_request)
    print("deposite enquiry response:",response)

    print("\n\transaction_status_req_url", transaction_status_req_url)
    print("\n\transaction_status_xml_request", transaction_status_xml_request)
    response = bill_avenue_req(transaction_status_req_url, transaction_status_xml_request)
    print("transaction status response:",response)

    # ccavenue_payment_req()
