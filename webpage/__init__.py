from flask import Flask, request, render_template, jsonify
import random
from data import db_session
from data.user import User

from amocrm.v2 import tokens, Lead, custom_field, Contact as _Contact

app = Flask(__name__, static_folder='assets')

_gift = 'none'

class Contact(_Contact):
    gift = custom_field.TextCustomField('Подарок', field_id='secret')
    notcustom_phone = custom_field.TextCustomField('Раб. тел.', field_id='secret')
    select = custom_field.SelectCustomField('Источник обращения', field_id='secret')


@app.route('/', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        global _gift
        db_sess = db_session.create_session()
        gifts = ['comp', 'cert', 'consult']
        gift = random.choice(gifts)
        _gift = gift

        all_phones = [x.phone_number for x in db_sess.query(User).all()]

        lead = Lead.objects.create(pipeline_id=7293886, name='Заявка с лендинга по имплантации')
        lead.save()

        a = Lead.objects.get(object_id=lead.id)
        cont = Contact.objects.create(name=f"{request.form['Имя']} | {request.form['Телефон']}")
        a.contacts.append(cont)
        a.save()

        contact = Contact.objects.get(object_id=cont.id)
        contact.notcustom_phone = request.form['Телефон']
        contact.select = 'Лендинг Имплантация'

        if request.form['Телефон'] not in all_phones:
            if gift == 'comp':
                contact.gift = 'Компьютерная томография'
            elif gift == 'cert':
                contact.gift = '2000 рублей на любую процедуру'
            elif gift == 'consult':
                contact.gift = 'Консультация хирурга-имплантолога'
        else:
            _gift = 'none'
        
        user = User(name=request.form['Имя'], phone_number=request.form['Телефон'])
        if request.form['Телефон'] not in all_phones:
            user.gifts = gift
        db_sess.add(user)

        contact.save()
        db_sess.commit()

    return render_template('index.html')


@app.route('/get_gift', methods=["GET"])
def new():
    return jsonify({'gift': _gift})


def main():
    tokens.default_token_manager(
        client_id="secret",
        client_secret="secret",
        subdomain="secret",
        redirect_url="secret",
        storage=tokens.FileTokensStorage(), 
    )

    db_session.global_init('db/db.sqlite')
    app.run()


if __name__ == '__main__':
    main()
    