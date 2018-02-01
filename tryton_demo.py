#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys
import random
from itertools import chain

from proteus import Model, Wizard
from proteus import config as pconfig

TODAY = datetime.date.today()


def set_config(database):
    return pconfig.set_trytond(database)


def activate_modules(config, modules):
    Module = Model.get('ir.module')
    modules = Module.find([
            ('name', 'in', modules),
            ])
    for module in modules:
        if module.state == 'activated':
            module.click('upgrade')
        else:
            module.click('activate')
    modules = [x.name for x in Module.find([('state', '=', 'to activate')])]
    Wizard('ir.module.activate_upgrade').execute('upgrade')

    ConfigWizardItem = Model.get('ir.module.config_wizard.item')
    for item in ConfigWizardItem.find([('state', '!=', 'done')]):
        item.state = 'done'
        item.save()

    activated_modules = [m.name
        for m in Module.find([('state', '=', 'activated')])]
    return modules, activated_modules


def setup_party(config, modules):
    Party = Model.get('party.party')
    Address = Model.get('party.address')
    Country = Model.get('country.country')
    Subdivision = Model.get('country.subdivision')
    ContactMechanism = Model.get('party.contact_mechanism')

    customers, suppliers = [], []

    ar, = Country.find([('code', '=', 'AR')])
    caba, = Subdivision.find([('code', '=', 'AR-C')])
    santa_fe, = Subdivision.find([('code', '=', 'AR-S')])

    name = 'Museo Nacional de Bellas Artes'
    try:
        party, = Party.find([('name', '=', name)])
    except ValueError:
        party = Party(name=name)
        party.addresses.pop()
        party.addresses.append(Address(street='Av. Libertador 1555',
                zip='1503', city='Ciudad Autonoma de Buenos Aires', country=ar,
                subdivision=caba))
        party.contact_mechanisms.append(ContactMechanism(type='phone',
                value='(011) 963-6590'))
        party.contact_mechanisms.append(ContactMechanism(type='website',
                value='https://www.bellasartes.gob.ar/'))
        party.vat_number = '30714248169'
        party.iva_condition = 'responsable_inscripto'
        party.save()
    customers.append(party)

    name = 'Biblioteca Utopia'
    try:
        party, = Party.find([('name', '=', name)])
    except ValueError:
        party = Party(name=name)
        party.addresses.pop()
        party.addresses.append(Address(street='Corrientes 1543',
                zip='1506', city='Ciudad Autonoma de Buenos Aires', country=ar,
                subdivision=caba))
        party.contact_mechanisms.append(ContactMechanism(type='phone',
                value='(011) 348-3000'))
        party.contact_mechanisms.append(ContactMechanism(type='website',
                value='http://www.centrocultural.coop/'))
        party.vat_number = '30518428264'
        party.iva_condition = 'responsable_inscripto'
        party.save()
    customers.append(party)

    name = "Calixto Cafe y Bistro"
    try:
        party, = Party.find([('name', '=', name)])
    except ValueError:
        party = Party(name=name)
        party.addresses.pop()
        party.addresses.append(Address(street='Catamarca 2127',
                zip='1509', city='Rosario', country=ar,
                subdivision=santa_fe))
        party.contact_mechanisms.append(ContactMechanism(type='phone',
                value='(341) 346-6883'))
        party.vat_number = '30712374310'
        party.iva_condition = 'responsable_inscripto'
        party.save()
    customers.append(party)

    name = "Saber"
    try:
        party, = Party.find([('name', '=', name)])
    except ValueError:
        party = Party(name=name)
        party.vat_number = '30714546178'
        party.iva_condition = 'responsable_inscripto'
        party.save()
    suppliers.append(party)

    return customers, suppliers


def setup_company(config):
    Party = Model.get('party.party')
    Company = Model.get('company.company')
    Currency = Model.get('currency.currency')
    Country = Model.get('country.country')

    ars, = Currency.find([('code', '=', 'ARS')])
    ar, = Country.find([('code', '=', 'AR')])

    company_config = Wizard('company.company.config')
    company_config.execute('company')
    company = company_config.form
    party = Party(name='Union Papelera Platense')
    party.vat_number = '30709170046'
    party.iva_condition = 'responsable_inscripto'
    party.save()
    company.party = party
    company.currency = ars
    company_config.execute('add')

    # Reload context
    User = Model.get('res.user')
    config._context = User.get_preferences(True, config.context)

    company, = Company.find()
    return company


def setup_company_post(config, company):
    Party = Model.get('party.party')
    Company = Model.get('company.company')
    Currency = Model.get('currency.currency')
    Address = Model.get('party.address')
    Country = Model.get('country.country')
    Subdivision = Model.get('country.subdivision')
    Employee = Model.get('company.employee')

    ars, = Currency.find([('code', '=', 'ARS')])
    ar, = Country.find([('code', '=', 'AR')])

    party_scott = Party(name='Roberto Owen')
    party_scott.vat_number = '20060304956'
    party_scott.iva_condition = 'monotributo'
    party_scott.save()
    Employee(party=party_scott, company=company).save()
    party_beesly = Party(name='Guillermo King')
    party_beesly.vat_number = '27060304950'
    party_beesly.iva_condition = 'monotributo'
    party_beesly.save()
    Employee(party=party_beesly, company=company).save()
    party_howard = Party(name='Felipe Fourier')
    party_howard.vat_number = '20112055011'
    party_howard.iva_condition = 'monotributo'
    party_howard.save()
    Employee(party=party_howard, company=company).save()

    dmi = Company()
    party_dmi = Party(name='Papelera Silplast')
    address = Address()
    party_dmi.addresses.append(address)
    address.city = 'La Plata'
    address.country = ar
    address.subdivision, = Subdivision.find([('code', '=', 'AR-B')])
    party_dmi.vat_number = '30714324655'
    party_dmi.iva_condition = 'responsable_inscripto'
    party_dmi.save()
    dmi.party = party_dmi
    dmi.currency = ars
    dmi.save()

    dms = Company()
    party_dms = Party(name='Papelera Silplast Resistencia')
    address = Address()
    party_dms.addresses.append(address)
    address.city = 'Resistencia'
    address.country = ar
    address.subdivision, = Subdivision.find([('code', '=', 'AR-H')])
    party_dms.vat_number = '30610459834'
    party_dms.iva_condition = 'responsable_inscripto'
    party_dms.save()
    dms.party = party_dms
    dms.currency = ars
    dms.parent = dmi
    dms.save()

    party_halper = Party(name='Jorge Leandro Perez')
    party_halper.vat_number = '20119851964'
    party_halper.iva_condition = 'monotributo'
    party_halper.save()
    Employee(party=party_halper, company=dms).save()
    party_schrute = Party(name='Nicolas Gutierrez')
    party_schrute.vat_number = '23082897399'
    party_schrute.iva_condition = 'monotributo'
    party_schrute.save()
    Employee(party=party_schrute, company=dms).save()
    party_martin = Party(name='Angela Lopez')
    party_martin.vat_number = '20283836178'
    party_martin.iva_condition = 'monotributo'
    party_martin.save()
    Employee(party=party_martin, company=dms).save()
    party_miner = Party(name='Floreal Gorini')
    party_miner.vat_number = '23241278719'
    party_miner.iva_condition = 'monotributo'
    party_miner.save()
    Employee(party=party_miner, company=dms).save()


def setup_account(config, modules, company):
    AccountTemplate = Model.get('account.account.template')
    Account = Model.get('account.account')
    FiscalYear = Model.get('account.fiscalyear')
    Sequence = Model.get('ir.sequence')
    SequenceStrict = Model.get('ir.sequence.strict')

    root_template, = AccountTemplate.find([
        ('parent', '=', None),
        ('name', '=', 'Plan Contable Argentino para Cooperativas'),
        ])
    create_chart_account = Wizard('account.create_chart')
    create_chart_account.execute('account')
    create_chart_account.form.account_template = root_template
    create_chart_account.form.company = company
    create_chart_account.execute('create_account')

    receivable, = Account.find([
            ('kind', '=', 'receivable'),
            ('code', '=', '1135'),  # Deudores por ventas
            ('company', '=', company.id),
            ])
    payable, = Account.find([
            ('kind', '=', 'payable'),
            ('code', '=', '2111'),  # Proveedores
            ('company', '=', company.id),
            ])

    create_chart_account.form.account_receivable = receivable
    create_chart_account.form.account_payable = payable
    create_chart_account.execute('create_properties')

    for start_date in (TODAY + relativedelta(month=1, day=1, years=-1),
            TODAY + relativedelta(month=1, day=1),
            TODAY + relativedelta(month=1, day=1, years=1)):
        fiscalyear = FiscalYear(name='%s' % start_date.year)
        fiscalyear.start_date = start_date
        fiscalyear.end_date = start_date + relativedelta(month=12, day=31)
        fiscalyear.company = company
        post_move_sequence = Sequence(name='%s' % start_date.year,
            code='account.move',
            company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence
        if 'account_invoice' in modules:
            for attr, name in (('out_invoice_sequence', 'Factura'),
                    ('in_invoice_sequence', 'Factura Proveedor'),
                    ('out_credit_note_sequence', 'Nota de Credito'),
                    ('in_credit_note_sequence', 'Nota de credito proveedor')):
                sequence = SequenceStrict(
                    name='%s %s' % (name, start_date.year),
                    code='account.invoice',
                    company=company)
                sequence.save()
                setattr(fiscalyear, attr, sequence)
        if 'account_voucher_ar' in modules:
            sequence = Sequence(
                name='%s %s' % ('Recibo de Pago', start_date.year),
                code='account.voucher.payment',
                company=company)
            sequence.save()
            setattr(fiscalyear, 'payment_sequence', sequence)
            sequence = Sequence(
                name='%s %s' % ('Recibo de Cobro', start_date.year),
                code='account.voucher.receipt',
                company=company)
            sequence.save()
            setattr(fiscalyear, 'receipt_sequence', sequence)
        if 'cooperative_ar' in modules:
            sequence = Sequence(
                name='%s %s' % ('Recibo comprobante cooperativa', start_date.year),
                code='account.cooperative.receipt',
                company=company)
            sequence.save()
            setattr(fiscalyear, 'cooperative_receipt_sequence', sequence)
        fiscalyear.save()
        FiscalYear.create_period([fiscalyear.id], config.context)


def setup_product(config, modules, company=None):
    ProductTemplate = Model.get('product.template')
    Category = Model.get('product.category')
    Uom = Model.get('product.uom')

    if 'account_product' in modules:
        Account = Model.get('account.account')
        expense, = Account.find([
                ('kind', '=', 'expense'),
                ('code', '=', '5249'),  # Gastos Varios
                ('company', '=', company.id),
                ])
        revenue, = Account.find([
                ('kind', '=', 'revenue'),
                ('code', '=', '515'),  # Ingresos por Ventas
                ('company', '=', company.id),
                ])

    papers = Category(name='Papeles')
    if 'account_product' in modules:
        papers.account_expense = expense
        papers.account_revenue = revenue
    papers.save()

    sizes = {}
    for format in ('A5', 'A4', 'A3', 'Carta', 'Legal', 'Libro mayor'):
        size = Category(name=format, parent=papers)
        if 'account_product' in modules:
            size.account_expense = expense
            size.account_revenue = revenue
        size.save()
        sizes[format] = size

    unit, = Uom.find([('name', '=', 'Unit')])

    margin = Decimal('1.01')
    for quantity in (250, 500, 1000, 2500):
        for format, category in sizes.iteritems():
            paper_template = ProductTemplate(name='%s Papel %s'
                % (format, quantity))
            paper_template.category = category
            paper_template.default_uom = unit
            paper_template.type = 'goods'
            paper_template.list_price = (Decimal('0.02') * quantity * margin
                ).quantize(Decimal('0.0001'))
            paper_template.cost_price = Decimal('0.01') * quantity
            if 'account_product' in modules:
                paper_template.account_expense = expense
                paper_template.account_revenue = revenue
            if 'sale' in modules:
                paper_template.salable = True
            if 'purchase' in modules:
                paper_template.purchasable = True
            paper_template.save()
        margin *= margin


def setup_account_invoice(config, modules, company):
    Party = Model.get('party.party')
    PaymentTerm = Model.get('account.invoice.payment_term')

    payment_term = PaymentTerm(name='30 dias')
    line = payment_term.lines.new()
    line.type = 'remainder'
    delta = line.relativedeltas.new()
    delta.days = 30
    payment_term.save()

    parties = Party.find()
    Party.write([p.id for p in parties], {
            'customer_payment_term': payment_term.id,
            'supplier_payment_term': payment_term.id,
            }, config.context)


def setup_account_invoice_ar(config, modules, company):
    Pos = Model.get('account.pos')
    PosSequence = Model.get('account.pos.sequence')
    Sequence = Model.get('ir.sequence')

    punto_de_venta = Pos()
    punto_de_venta.pos_type = 'manual'
    punto_de_venta.number = 2
    punto_de_venta.save()

    for attr, name in (
	    ('1', '01-Factura A'),
            ('3', '03-Nota de Credito A'),
            ('6', '06-Factura B'),
            ('8', '08-Nota de Credito B'),
            ('11', '11-Factura C'),
            ('13', '13-Nota de Credito C')):
        sequence = Sequence(
            name='%s %s' % (name, 'manual'),
            code='account.invoice',
            company=company)
        sequence.save()
        pos_sequence = PosSequence()
        pos_sequence.invoice_type = attr
        pos_sequence.invoice_sequence = sequence
        pos_sequence.pos = punto_de_venta
        pos_sequence.save()

    return punto_de_venta


def setup_account_invoice_post(config, modules, company):
    Invoice = Model.get('account.invoice')

    invoices = Invoice.find([
            ('type', '=', 'out'),
            ('state', 'in', ['draft', 'validated']),
            ])
    invoices = random.sample(invoices, len(invoices) * 2 / 3)
    invoices = list(chain(*zip(invoices,
                Invoice.find([
                        ('type', '=', 'in'),
                        ('state', 'in', ['draft', 'validated']),
                        ]))))

    invoice_date = TODAY + relativedelta(months=-1)
    i = j = 0
    while invoice_date <= TODAY:
        j = random.randint(1, 5)
        for invoice in invoices[i:i + j]:
            invoice.invoice_date = invoice_date
            invoice.save()
        i += j
        invoice_date += relativedelta(days=random.randint(1, 3))
    Invoice.post([inv.id for inv in invoices[0:i]], config.context)

def setup_account_voucher_ar(config, modules, company):
    Currency = Model.get('currency.currency')
    Sequence = Model.get('ir.sequence')
    Journal = Model.get('account.journal')
    Line = Model.get('account.move.line')
    AccountVoucher = Model.get('account.voucher')
    Account = Model.get('account.account')
    AccountVoucherPayMode = Model.get('account.voucher.paymode')
    AccountVoucherLinePaymode = Model.get('account.voucher.line.paymode')

    ars, = Currency.find([('code', '=', 'ARS')])
    bank, = Account.find([
            ('code', '=', '11141'), # Banco
            ('company', '=', company.id),
            ])

    try:
        journal, = Journal.find([('name', '=', 'Banco')])
    except ValueError:
        sequence = Sequence(name='Banco', code='account.journal',
            company=company)
        sequence.save()
        journal = Journal(name='Banco', type='cash', credit_account = bank,
        debit_account = bank, sequence=sequence)
        journal.save()

    try:
        paymode, = AccountVoucherPayMode.find([
                ('name', '=', 'Acreditacion Banco')])
    except ValueError:
        paymode = AccountVoucherPayMode(name='Acreditacion Banco', account=bank)
        paymode.save()


    move_lines = Line.find([
            ('account.kind', '=', 'receivable'),
            ('party', '!=', None),
            ('reconciliation', '=', None),
            ('state', '=', 'valid'),
            ('move.state', '=', 'posted'),
            #('payment_amount', '!=', 0),
            ])
    move_lines = random.sample(move_lines, len(move_lines) * 2 / 3)
    if not move_lines:
        return

    for line in move_lines:
        voucher = AccountVoucher()
        voucher.currency = ars
        voucher.date = datetime.date.today()
        voucher.voucher_type = 'receipt'
        voucher.journal = journal
        voucher.party = line.origin.party
        del voucher.lines[1:]
        payment_line = voucher.lines[0]
        payment_line.amount = payment_line.amount_unreconciled
        payment_line.save()
        voucher.save()
        paymode_line = AccountVoucherLinePaymode(voucher=voucher, pay_mode=paymode,
            pay_amount = payment_line.amount_unreconciled)
        paymode_line.save()
        voucher.click('post')

def setup_account_payment(config, modules, company):
    Currency = Model.get('currency.currency')
    Journal = Model.get('account.payment.journal')
    Line = Model.get('account.move.line')
    Payment = Model.get('account.payment')

    usd, = Currency.find([('code', '=', 'USD')])
    journal = Journal(name='Manual', currency=usd, company=company,
        process_method='manual')
    journal.save()

    lines = Line.find([
            ('account.kind', '=', 'payable'),
            ('party', '!=', None),
            ('reconciliation', '=', None),
            ('payment_amount', '!=', 0),
            ])
    lines = random.sample(lines, len(lines) * 2 / 3)
    if not lines:
        return

    pay_line = Wizard('account.move.line.pay', lines)
    pay_line.form.journal = journal
    pay_line.execute('start')

    payments = Payment.find([])
    payments = random.sample(payments, len(payments) * 2 / 3)

    for payment in payments:
        payment.click('approve')

    payments = random.sample(payments, len(payments) * 2 / 3)
    i = j = 0
    while i < len(payments):
        j = random.randint(1, 5)
        process = Wizard('account.payment.process', payments[i:i + j])
        process.execute('process')
        i += j


def setup_account_statement(config, modules, company):
    Journal = Model.get('account.statement.journal')
    Statement = Model.get('account.statement')
    AccountJournal = Model.get('account.journal')
    Account = Model.get('account.account')
    Sequence = Model.get('ir.sequence')
    Invoice = Model.get('account.invoice')

    sequence = Sequence(name='Statement',
        code='account.journal',
        company=company)
    sequence.save()

    cash, = Account.find([
            #('name', '=', 'Main Cash'),
	    ('code', '=', '1111'), # Caja
            ('company', '=', company.id),
            ])

    account_journal = AccountJournal(name='Banco',
        type='statement',
        credit_account=cash,
        debit_account=cash,
        sequence=sequence)
    account_journal.save()

    journal = Journal(name='Banco',
        journal=account_journal,
        validation='balance')
    journal.save()

    invoices = Invoice.find([
            ('state', '=', 'posted'),
            ])
    invoices = random.sample(invoices, len(invoices) * 2 / 3)

    total_amount = Decimal(0)
    statement = Statement(name='001',
        journal=journal,
        start_balance=Decimal(0))
    for i, invoice in enumerate(invoices):
        if not invoice.amount_to_pay:
            continue
        line = statement.lines.new()
        line.number = str(i)
        line.date = invoice.invoice_date + relativedelta(
            days=random.randint(1, 20))
        amount = invoice.amount_to_pay
        if invoice.type in ('in_invoice', 'out_credit_note'):
            amount = - amount
        line.amount = amount
        line.party = invoice.party
        if random.random() < 2. / 3.:
            line.invoice = invoice
        total_amount += line.amount

    statement.end_balance = total_amount
    statement.click('validate_statement')

def setup_sale_pos_ar(config, modules, pos):
    Configuration = Model.get('sale.configuration')
    config, = Configuration.find([])
    config.pos = pos
    config.save()

def setup_sale(config, modules, company, customers):
    Sale = Model.get('sale.sale')
    Product = Model.get('product.product')

    all_products = Product.find([
            ('salable', '=', True),
            ])
    sale_date = TODAY + relativedelta(months=-2)
    while sale_date <= TODAY + relativedelta(days=10):
        for _ in range(random.randint(1, 5)):
            customer = random.choice(customers)
            sale = Sale()
            sale.party = customer
            sale.sale_date = sale_date
            #sale.pos = pos
            #sale.on_change_party()
            products = random.sample(all_products, 5)
            for product in products:
                sale_line = sale.lines.new()
                sale_line.product = product
                sale_line.quantity = random.randint(1, 50)
            sale.save()
            if sale_date <= TODAY:
                threshold = 2. / 3.
            else:
                threshold = 1. / 3.
            if random.random() <= threshold:
                sale.click('quote')
                if random.random() <= threshold:
                    sale.click('confirm')
                    if random.random() <= threshold:
                        sale.click('process')
                elif random.random() >= threshold:
                    sale.click('cancel')
            elif random.random() >= threshold:
                sale.click('cancel')
        sale_date += relativedelta(days=random.randint(1, 3))


def setup_purchase(config, modules, company, suppliers):
    Purchase = Model.get('purchase.purchase')
    Product = Model.get('product.product')

    all_products = Product.find([
            ('purchasable', '=', True),
            ])
    purchase_date = TODAY - relativedelta(days=60)
    while purchase_date <= TODAY + relativedelta(days=20):
        supplier = random.choice(suppliers)
        purchase = Purchase()
        purchase.party = supplier
        purchase.purchase_date = purchase_date
        products = random.sample(all_products, random.randint(1, 15))
        for product in products:
            purchase_line = purchase.lines.new()
            purchase_line.product = product
            purchase_line.quantity = random.randint(20, 100)
        purchase.save()
        threshold = 2. / 3.
        if random.random() <= threshold:
            purchase.click('quote')
            if random.random() <= threshold:
                purchase.click('confirm')
                purchase.click('process')
        elif random.choice([True, False]):
            purchase.click('cancel')
        purchase_date += relativedelta(days=random.randint(5, 10))


def setup_stock(config, activated, company, suppliers):
    ShipmentIn = Model.get('stock.shipment.in')
    ShipmentOut = Model.get('stock.shipment.out')

    for supplier in suppliers:
        shipment = ShipmentIn()
        shipment.supplier = supplier
        all_moves = shipment.incoming_moves.find()
        moves = random.sample(all_moves, len(all_moves) * 2 / 3)
        while moves:
            shipment = ShipmentIn()
            shipment.supplier = supplier
            for _ in range(random.randint(1, len(moves))):
                move = moves.pop()
                shipment.incoming_moves.append(move)
            shipment.click('receive')
            shipment.click('done')

    shipments = ShipmentOut.find([('state', '=', 'waiting')])
    for shipment in shipments:
        if ShipmentOut.assign_try([shipment.id], config.context):
            shipment.click('pack')
            shipment.click('done')


def setup_project(config, activated, company, customers):
    Work = Model.get('project.work')

    customer_projects = {
            'Website': ['analysis', 'design', 'setup'],
            'Labels': ['design'],
            'Calendar': ['design'],
            }

    for name, task_names in customer_projects.iteritems():
        project = Work(name=name, type='project', timesheet_available=False)
        project.party = random.choice(customers)
        for task_name in task_names:
            task = Work(name=task_name, type='task', timesheet_available=True)
            task.effort_duration = datetime.timedelta(
                    hours=random.randint(1, 5))
            task.progress = random.randint(1, 100) // 5 * 5 / 100.
            project.children.append(task)
        project.save()


def setup_timesheet(config, activated, company):
    Work = Model.get('timesheet.work')
    Employee = Model.get('company.employee')
    Line = Model.get('timesheet.line')

    for name in ['Marketing', 'Accounting', 'Secretary']:
        work = Work(name=name)
        work.save()

    employees = Employee.find([('company', '=', company.id)])
    works = Work.find([])

    date = TODAY + relativedelta(months=-1)
    day = datetime.timedelta(hours=8)
    while date <= TODAY:
        if date.weekday() < 5:
            for employee in employees:
                total = datetime.timedelta()
                while total < day:
                    if random.random() > 0.8:
                        break
                    line = Line(employee=employee, date=date)
                    line.work = random.choice(works)
                    duration = datetime.timedelta(hours=random.randint(1, 8))
                    line.duration = min(duration, day - total)
                    line.save()
        date += datetime.timedelta(days=1)


def setup_production(config, activated, company):
    BOM = Model.get('production.bom')
    Production = Model.get('production')
    ProductTemplate = Model.get('product.template')
    Uom = Model.get('product.uom')

    unit, = Uom.find([('name', '=', 'Unit')])

    if 'account_product' in activated:
        Account = Model.get('account.account')
        expense, = Account.find([
                ('kind', '=', 'expense'),
                ('code', '=', '5249'),  # Gastos Varios
                ('company', '=', company.id),
                ])
        revenue, = Account.find([
                ('kind', '=', 'revenue'),
                ('code', '=', '515'),  # Ingresos por Ventas
                ('company', '=', company.id),
                ])

    def create_product(name, list_price, cost_price):
        template = ProductTemplate(name=name)
        template.default_uom = unit
        template.type = 'goods'
        template.list_price = list_price
        template.cost_price = cost_price
        if 'account_product' in activated:
            template.account_expense = expense
            template.account_revenue = revenue
        template.save()
        return template.products[0]

    bom = BOM(name='Computer rev1')

    input_ = bom.inputs.new()
    tower = create_product('Tower', Decimal(400), Decimal(250))
    input_.product = tower
    input_.quantity = 1

    input_ = bom.inputs.new()
    input_.product = create_product('Keyboard', Decimal(30), Decimal(10))
    input_.quantity = 1

    input_ = bom.inputs.new()
    input_.product = create_product('Mouse', Decimal(10), Decimal(5))
    input_.quantity = 1

    input_ = bom.inputs.new()
    input_.product = create_product('Screen', Decimal(300), Decimal(200))
    input_.quantity = 1

    output = bom.outputs.new()
    computer = create_product('Computer', Decimal(750), Decimal(465))
    output.product = computer
    output.quantity = 1

    bom.save()
    computer.boms.new(bom=bom)
    computer.save()

    if 'production_routing' in activated:
        setup_production_routing(config, activated, company)

    if 'production_work' in activated:
        WorkCenter = Model.get('production.work.center')
        WorkCycle = Model.get('production.work.cycle')
        setup_production_work(config, activated, company)
        work_centers = WorkCenter.find([('parent', '=', None)])

    production_date = TODAY + relativedelta(months=-1)
    while production_date <= TODAY + relativedelta(days=20):
        for _ in range(random.randint(0, 3)):
            production = Production()
            production.effective_date = production_date
            production.product = computer
            production.quantity = random.randint(1, 40)
            production.bom = computer.boms[0].bom

            if 'production_routing' in activated:
                production.routing = computer.boms[0].routing

            if 'production_work' in activated:
                production.work_center = random.choice(work_centers)

            production.save()

            if (production_date < TODAY) or (random.random() <= 1. / 3.):
                production.click('wait')
                if production_date < TODAY:
                    production.click('assign_force')
                    production.click('run')
                    if random.random() <= 2. / 3.:
                        if 'production_work' in activated:
                            for work in production.works:
                                for _ in range(0, random.randint(1, 2)):
                                    cycle = WorkCycle(
                                        work=work,
                                        duration=datetime.timedelta(
                                            seconds=random.randint(60, 3600)),
                                        )
                                    cycle.save()
                                    cycle.click('run')
                                    cycle.click('do')
                        output, = production.outputs
                        output.unit_price = (production.cost
                            / Decimal(production.quantity)
                            ).quantize(Decimal('0.0001'))
                        production.click('done')
            production_date += relativedelta(days=random.randint(1, 3))


def setup_production_routing(config, activated, company):
    Routing = Model.get('production.routing')
    Operation = Model.get('production.routing.operation')
    Product = Model.get('product.product')

    routing = Routing(name='Computer routing rev1')

    operation1 = Operation(name='Assemble pieces')
    operation1.save()
    step1 = routing.steps.new()
    step1.operation = operation1

    operation2 = Operation(name='Install software')
    operation2.save()
    step2 = routing.steps.new()
    step2.operation = operation2

    operation3 = Operation(name='Test')
    operation3.save()
    step3 = routing.steps.new()
    step3.operation = operation3

    operation4 = Operation(name='Package')
    operation4.save()
    step4 = routing.steps.new()
    step4.operation = operation4

    routing.boms.extend(routing.boms.find([('name', '=', 'Computer rev1')]))

    routing.save()

    computer, = Product.find([('name', '=', 'Computer')])
    bom, = computer.boms
    bom.routing = routing
    bom.save()


def setup_production_work(config, activated, company):
    WorkCenterCategory = Model.get('production.work.center.category')
    WorkCenter = Model.get('production.work.center')
    Operation = Model.get('production.routing.operation')

    assembly = WorkCenterCategory(name='Assembly')
    assembly.save()
    operation, = Operation.find([('name', '=', 'Assemble pieces')])
    operation.work_center_category = assembly
    operation.save()

    installation = WorkCenterCategory(name='Installation')
    installation.save()
    operations = Operation.find([
            ('name', 'in', ['Install software', 'Test']),
            ])
    for operation in operations:
        operation.work_center_category = installation
    Operation.save(operations)

    packaging = WorkCenterCategory(name='Packaging')
    packaging.save()
    operation, = Operation.find([('name', '=', 'Package')])
    operation.work_center_category = packaging
    operation.save()

    lines = []
    for i in range(1, 4):
        line = WorkCenter(name='Line %i' % i)

        assembly_line = line.children.new()
        assembly_line.name = 'Assembly Line %i' % i
        assembly_line.category = assembly
        assembly_line.cost_method = 'cycle'
        assembly_line.cost_price = Decimal(20)

        installation_line = line.children.new()
        installation_line.name = 'Installation Line %i' % i
        installation_line.category = installation
        installation_line.cost_method = 'hour'
        installation_line.cost_price = Decimal(15)

        packaging_line = line.children.new()
        packaging_line.name = 'Packaging Line %i' % i
        packaging_line.category = packaging
        packaging_line.cost_method = 'hour'
        packaging_line.cost_price = Decimal(10)

        lines.append(line)
    WorkCenter.save(lines)


def setup_languages(config, modules, demo_password, company=None):
    Lang = Model.get('ir.lang')
    Module = Model.get('ir.module')
    User = Model.get('res.user')
    Group = Model.get('res.group')
    Action = Model.get('ir.action')

    langs = Lang.find([
            ('code', '=', 'es'),
            ])
    Lang.write([x.id for x in langs], {
            'translatable': True,
            }, config.context)
    Module.upgrade([x.id for x in Module.find([('name', 'in', modules)])],
        config.context)
    Wizard('ir.module.activate_upgrade').execute('upgrade')

    menu, = Action.find([('usage', '=', 'menu')])
    for lang in langs:
        if lang.code == 'en':
            name = 'Demo'
            login = 'demo'
        else:
            if lang.code[:2] != lang.code[-2:].lower():
                continue
            name = 'Demo %s' % lang.name
            login = 'demo_%s' % lang.code[:2]
        try:
            user, = User.find([('login', '=', login)])
        except ValueError:
            user = User()
        user.name = name
        user.login = login
        user.password = demo_password
        groups = Group.find([
                ('name', 'not ilike', '%Admin%'),
                ])
        user.groups.extend(groups)
        user.language = lang
        user.menu = menu
        if company:
            user.main_company = company
            user.company = company
        user.save()


def main(database, modules, demo_password):
    config = set_config(database)
    to_activate, activated = activate_modules(config, modules)

    if ('party' in to_activate
            or 'sale' in to_activate
            or 'purchase' in to_activate
            or 'stock' in activated):
        customers, suppliers = setup_party(config, modules)

    if 'company' in to_activate:
        company = setup_company(config)
    elif 'company' in activated:
        Company = Model.get('company.company')
        company, = Company.find([
                ('party.name', '=', 'Michael Scott Paper Company'),
                ])
    else:
        company = None

    if 'account' in to_activate:
        setup_account(config, activated, company)

    if 'company' in to_activate:
        setup_company_post(config, company)

    if 'product' in to_activate:
        setup_product(config, activated, company=company)

    if 'account_invoice' in to_activate:
        setup_account_invoice(config, activated, company)

    if 'account_invoice_ar' in to_activate:
        pos = setup_account_invoice_ar(config, activated, company)

    if 'sale' and 'sale_pos_ar' in to_activate:
        setup_sale_pos_ar(config, activated, pos)

    if 'sale' in to_activate:
        setup_sale(config, activated, company, customers)

    if 'purchase' in to_activate:
        setup_purchase(config, activated, company, suppliers)

    if 'stock' in to_activate:
        setup_stock(config, activated, company, suppliers)

    if 'account_invoice' in activated:
        setup_account_invoice_post(config, activated, company)

    #if 'account_payment' in installed:
    #    setup_account_payment(config, installed, company)

    if 'account_voucher_ar' in to_activate:
        setup_account_voucher_ar(config, activated, company)

    if 'account_statement' in to_activate:
        setup_account_statement(config, activated, company)

    if 'project' in activated:
        setup_project(config, activated, company, customers)

    if 'timesheet' in activated:
        setup_timesheet(config, activated, company)

    if 'production' in to_activate:
        setup_production(config, activated, company)

    setup_languages(config, to_activate, demo_password, company=company)

if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--module', dest='modules', nargs='+',
        help='module to install', default=[
            'account',
            'account_invoice',
            #'account_payment',
            'account_statement',
            'company',
            'party',
            'product',
            'purchase',
            'sale',
            'stock',
            'project',
            'timesheet',
            'production',
            'production_routing',
            'production_work',
            'account_coop_ar',
            'party_ar',
            'account_voucher_ar',
            'account_check_ar',
            'account_retencion_ar',
            #'company_logo',
            'account_invoice_ar',
            'sale_pos_ar',
            'subdiario',
            'citi_afip',
            'current_account',
            'recover_invoice_ar',
            'bank_ar',
            'account_invoice_visible_payments',
            'project_invoice',
            'analytic_account',
            'analytic_invoice',
            'analytic_sale',
            'analytic_purchase',
            ])
    parser.add_argument('--demo_password', dest='demo_password',
        default='demo', help='demo password')
    parser.add_argument('-d', '--database', dest='database',
        default='demo', help="database name")
    options = parser.parse_args()
    sys.argv = []  # clean argv for trytond
    main(options.database, options.modules, options.demo_password)
