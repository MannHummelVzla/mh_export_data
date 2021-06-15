# -*- coding: utf-8 -*-

import base64
import datetime
import time

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ExportDataCsv(models.Model):
    _name = "export.data.csv"
    _description = "Export data in csv"
    _order = "date_start desc"

    AVAILABLE_STATES = [
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("cancel", "Cancelled"),
    ]

    name = fields.Char(string="Name", index=True, required=True)
    state = fields.Selection(
        AVAILABLE_STATES, string="Status", required=True, default="draft"
    )
    date_start = fields.Datetime(string="Date")
    downloaded = fields.Boolean(string="Downloaded", default=False)
    line_ids = fields.One2many(
        "export.data.csv.line", "export_id", string="Export Data Lines"
    )

    @api.model
    def generate_partner_csv(self, filter_rank):
        """Return string with data
        """
        result = {}
        cst_string = ""
        total_rows = 0
        start_id = 0
        last_id = 0
        mod_name = "res.partner"

        # supplier_rank | customer_rank
        filter = ''
        if filter_rank == 'supplier':
            filter = 'AND p.supplier_rank > 0'
            mod_name = "res.partner:supplier"

        if filter_rank == 'customer':
            filter = 'AND p.customer_rank> 0'
            mod_name = "res.partner:customer"

        modules = self.env["export.module.line"].search(
            [("name", "=", mod_name), ("export_data", "=", True)]
        )
        if modules:
            module = modules[0]
            start_id = module.last_id

            sql = """
            SELECT  p.id,p.name
            FROM    res_partner AS p
            WHERE p.id > %d %s
            ORDER BY p.id;""" % (int(start_id), filter)
            self._cr.execute(sql)
            rows = self._cr.fetchall()
            if rows:
                cst_string = cst_string + "code" + "\t" + "name" + "\t" + "zone" + "\t\n"
                for row in rows:
                    pname = ''
                    supplier = ''
                    customer = ''
                    total_rows += 1
                    last_id = row[0]
                    pid = row[0]
                    if row[1]:
                        pname = row[1]
                    cst_string = cst_string + " " + "\t" + pname + "\t" +  " " + "\t\n"
                result = {
                    "data": cst_string,
                    "module": mod_name,
                    "total_rows": total_rows,
                    "last_id": last_id,
                }
        return result

    @api.model
    def generate_currency_bs_csv(self):
        """Return string with data
        """
        result = {}
        cst_string = ""
        total_rows = 0
        start_id = 0
        last_id = 0
        modules = self.env["export.module.line"].search(
            [("name", "=", "res.currency"), ("export_data", "=", True)]
        )
        if modules:
            module = modules[0]
            start_id = module.last_id

            sql = """
            SELECT  r.id,c.name,r.name,r.rate
            FROM    res_currency AS c
            INNER JOIN res_currency_rate AS r ON c.id=r.currency_id
            WHERE c.currency_unit_label='Bolivar' and r.id > %d
            ORDER BY c.id;""" % int(start_id)
            self._cr.execute(sql)
            rows = self._cr.fetchall()
            if rows:
                cst_string = cst_string + "code" + "\t" + "date" + "\t" + "rate" + "\t\n"
                for row in rows:
                    code = ''
                    date = ''
                    rate = ''
                    total_rows += 1
                    last_id = row[0]
                    if row[1]:
                        code = row[1]
                    if row[2]:
                        date = row[2]
                    if row[3]:
                        rate = row[3]
                    cst_string = cst_string + code + "\t" + str(date) + "\t" + str(rate) + "\t\n"
                result = {
                    "data": cst_string,
                    "module": "res.currency",
                    "total_rows": total_rows,
                    "last_id": last_id,
                }
        return result

    @api.model
    def generate_purchase_order_csv(self):
        """Return string with data
        """
        result = {}
        cst_string = ""
        total_rows = 0
        start_id = 0
        last_id = 0
        modules = self.env["export.module.line"].search(
            [("name", "=", "purchase.order"), ("export_data", "=", True)]
        )
        if modules:
            module = modules[0]
            start_id = module.last_id

            sql = """
            SELECT  o.id,o.name,o.date_order,pp.default_code,l.product_qty,p.name
            FROM    purchase_order AS o
            INNER JOIN purchase_order_line AS l ON o.id=l.order_id
            INNER JOIN product_product AS pp ON l.product_id=pp.id
            INNER JOIN res_partner AS p ON o.partner_id=p.id
            WHERE  o.id > %d
            ORDER BY o.id;""" % int(start_id)
            self._cr.execute(sql)
            rows = self._cr.fetchall()
            if rows:
                cst_string = cst_string + "num_order" + "\t" + "date" + "\t" + "code_product" + "\t" + "product_qty" + "\t" + "partner_name" + "\t\n"
                for row in rows:
                    num_order = ''
                    date = ''
                    code_product = ''
                    product_qty = ''
                    partner_name = ''
                    total_rows += 1
                    last_id = row[0]
                    if row[1]:
                        num_order = row[1]
                    if row[2]:
                        date = row[2]
                    if row[3]:
                        code_product = row[3]
                    if row[4]:
                        product_qty = row[4]
                    if row[5]:
                        partner_name = row[5]
                    cst_string = cst_string + num_order + "\t" + str(date) + "\t" + code_product + "\t" + str(product_qty) + "\t" + partner_name + "\t\n"
                result = {
                    "data": cst_string,
                    "module": "purchase.order",
                    "total_rows": total_rows,
                    "last_id": last_id,
                }
        return result

    @api.model
    def generate_sale_order_csv(self):
        """Return string with data
        """
        result = {}
        cst_string = ""
        total_rows = 0
        start_id = 0
        last_id = 0
        modules = self.env["export.module.line"].search(
            [("name", "=", "sale.order:sale"), ("export_data", "=", True)]
        )
        if modules:
            module = modules[0]
            start_id = module.last_id

            sql = """
            SELECT  s.id,s.name,s.date_order,pp.default_code,l.product_uom_qty,p.name,c.name
            FROM    sale_order AS s
            INNER JOIN sale_order_line AS l ON s.id=l.order_id
            INNER JOIN product_product AS pp ON l.product_id=pp.id
            INNER JOIN res_partner AS p ON s.partner_id=p.id
            LEFT JOIN res_currency AS c ON l.currency_id=c.id
            WHERE  s.state='sale' AND s.id > %d
            ORDER BY s.id;""" % int(start_id)
            self._cr.execute(sql)
            rows = self._cr.fetchall()
            if rows:
                cst_string = cst_string + "num_order" + "\t" + "currency" + "\t" + "date" + "\t" + "code_product" + "\t" + "product_qty" + "\t" + "partner_name" + "\t\n"
                for row in rows:
                    num_order = ''
                    date = ''
                    code_product = ''
                    product_qty = ''
                    partner_name = ''
                    currency = ''
                    total_rows += 1
                    last_id = row[0]
                    if row[1]:
                        num_order = row[1]
                    if row[2]:
                        date = row[2]
                    if row[3]:
                        code_product = row[3]
                    if row[4]:
                        product_qty = row[4]
                    if row[5]:
                        partner_name = row[5]
                    if row[6]:
                        currency = row[6]
                    cst_string = cst_string + num_order + "\t" + currency + "\t" + str(date) + "\t" + code_product + "\t" + str(product_qty) + "\t" + partner_name + "\t\n"
                result = {
                    "data": cst_string,
                    "module": "sale.order:sale",
                    "total_rows": total_rows,
                    "last_id": last_id,
                }
        return result

    @api.model
    def generate_product_csv(self):
        """Return string with data
        """
        result = {}
        cst_string = ""
        total_rows = 0
        start_id = 0
        last_id = 0
        modules = self.env["export.module.line"].search(
            [("name", "=", "product.product"), ("export_data", "=", True)]
        )
        if modules:
            module = modules[0]
            start_id = module.last_id

            sql = """
            SELECT  p.id,p.default_code,t.name,t.type
            FROM    product_template AS t
            INNER JOIN product_product AS p ON t.id=p.product_tmpl_id
            WHERE t.sale_ok = true AND p.id > %d
            ORDER BY p.id;""" % int(start_id)
            self._cr.execute(sql)
            rows = self._cr.fetchall()
            if rows:
                cst_string = cst_string + "code" + "\t" + "name" + "\t" + "type" + "\t\n"
                for row in rows:
                    code = ''
                    name = ''
                    type = ''
                    total_rows += 1
                    last_id = row[0]
                    if row[1]:
                        code = row[1]
                    if row[2]:
                        name = row[2]
                    if row[3]:
                        type = row[3]
                    cst_string = cst_string + code + "\t" + name + "\t" + type + "\t\n"
                result = {
                    "data": cst_string,
                    "module": "product.product",
                    "total_rows": total_rows,
                    "last_id": last_id,
                }
        return result

    @api.model
    def generate_out_invoice_csv(self):
        """Return string with data
        """
        result = {}
        cst_string = ""
        total_rows = 0
        start_id = 0
        last_id = 0
        modules = self.env["export.module.line"].search(
            [("name", "=", "account.move:invoice"), ("export_data", "=", True)]
        )
        if modules:
            module = modules[0]
            start_id = module.last_id

            sql = """
            SELECT  m.id,m.name,m.invoice_origin,m.invoice_date,pp.default_code,l.quantity,l.price_total,p.name
            FROM    account_move AS m
            INNER JOIN account_move_line AS l ON m.id=l.move_id
            INNER JOIN product_product AS pp ON l.product_id=pp.id
            INNER JOIN res_partner AS p ON m.partner_id=p.id
            WHERE m.state='draft' AND m.id > %d
            ORDER BY m.id;""" % int(start_id)
            self._cr.execute(sql)
            rows = self._cr.fetchall()
            if rows:
                cst_string = cst_string + "num_order" + "\t" + "date" + "\t" + "code_product" + "\t" + "product_qty" + "\t" + "total" + "\t" + "partner_name" + "\t\n"
                for row in rows:
                    num_order = ''
                    date = ''
                    code_product = ''
                    product_qty = ''
                    partner_name = ''
                    total = 0
                    total_rows += 1
                    last_id = row[0]
                    if row[1] and row[1] != '/':
                        num_order = row[1] + ':'
                    if row[2]:
                        num_order += row[2]
                    if row[3]:
                        date = row[3]
                    if row[4]:
                        code_product = row[4]
                    if row[5]:
                        product_qty = row[5]
                    if row[6]:
                        total = row[6]
                    if row[7]:
                        partner_name = row[7]
                    cst_string = cst_string + num_order + "\t" + str(date) + "\t" + code_product + "\t" + str(product_qty) + "\t" +  str(total) + "\t" +partner_name + "\t\n"
                result = {
                    "data": cst_string,
                    "module": "account.move:invoice",
                    "total_rows": total_rows,
                    "last_id": last_id,
                }
        return result

    @api.model
    def _write_attachment(self, data, fname, export_id, model_name):
        """ """
        line_obj = self.env["export.data.csv.line"]
        fecha = time.strftime("%Y_%m_%d_%H%M%S")
        name = fname + "_" + fecha + "." + "csv"

        data_file = data.get("data", None)
        module = data.get("module", None)
        last_id = data.get("last_id", 0)
        record_count = data.get("total_rows", 0)
        csv_file = data_file.encode("utf-8")

        csv_file_id = (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": name,
                    "res_id": export_id,
                    "res_model": model_name,
                    "datas": base64.encodestring(csv_file),
                    "type": "binary",
                }
            )
        )

        line_obj.create(
            {
                "name": fname,
                "export_id": export_id,
                "last_id": last_id,
                "csv_file_id": csv_file_id.id,
                "record_count": record_count,
            }
        )
        modules = self.env["export.module.line"].search([("name", "=", module)])
        if modules:
            module = modules[0]
            module.write({"last_id": last_id, "record_count": record_count})
        if csv_file_id:
            return csv_file_id.id
        return False

    def action_generate_csv(self):
        """ """
        psdata = self.generate_partner_csv('supplier')
        if psdata:
            self._write_attachment(psdata, "Partner_Supplier", self.id, self._name)
        pcdata = self.generate_partner_csv('customer')
        if pcdata:
            self._write_attachment(pcdata, "Partner_Customer", self.id, self._name)
        cdata = self.generate_currency_bs_csv()
        if cdata:
            self._write_attachment(cdata, "Currency", self.id, self._name)
        ppdata = self.generate_product_csv()
        if ppdata:
            self._write_attachment(ppdata, "Product", self.id, self._name)
        sdata = self.generate_sale_order_csv()
        if sdata:
            self._write_attachment(sdata, "Sale", self.id, self._name)
        odata = self.generate_purchase_order_csv()
        if odata:
            self._write_attachment(odata, "Purchase", self.id, self._name)
        ftdata = self.generate_out_invoice_csv()
        if ftdata:
            self._write_attachment(ftdata, "Invoive", self.id, self._name)

        self.write({"state": "done"})

        return True

    def action_cron_generate_csv(self):
        now = datetime.datetime.now()
        export_obj = self.env["export.data.csv"]
        name = "Export Modules " + now.strftime("%m/%d/%Y, %H:%M:%S")
        instance = export_obj.create(
            {"name": name, "date_start": now, "state": "draft"}
        )

        psdata = instance.generate_partner_csv('supplier')
        if psdata:
            instance._write_attachment(psdata, "Partner_Supplier", instance.id, instance._name)

        pcdata = instance.generate_partner_csv('customer')
        if pcdata:
            instance._write_attachment(pcdata, "Partner_Customer", instance.id, instance._name)

        cdata = instance.generate_currency_bs_csv()
        if cdata:
            instance._write_attachment(cdata, "Currency", instance.id, instance._name)

        ppdata = instance.generate_product_csv()
        if ppdata:
            instance._write_attachment(ppdata, "Product", instance.id, instance._name)

        sdata = instance.generate_sale_order_csv()
        if sdata:
            instance._write_attachment(sdata, "Sale", self.id, self._name)

        odata = instance.generate_purchase_order_csv()
        if odata:
            instance._write_attachment(odata, "Purchase", self.id, self._name)

        ftdata = instance.generate_out_invoice_csv()
        if ftdata:
            instance._write_attachment(ftdata, "Invoive", self.id, self._name)


        instance.write({"state": "done"})

    def action_cron_sendmail_csv(self):
        mail_server = self.env["ir.mail_server"].search([("id", ">", 0)], limit=1)
        export_obj = self.env["export.data.csv"]
        config_param = self.env["ir.config_parameter"]
        now = datetime.datetime.now()
        att_ids = []

        name = "Export Modules " + now.strftime("%m/%d/%Y, %H:%M:%S")
        instance = export_obj.create(
            {"name": name, "date_start": now, "state": "draft"}
        )
        data = instance.generate_partner_csv()
        att_partner_id = instance._write_attachment(data, "Partner", instance.id, instance._name)
        instance.write({"state": "done"})
        att_ids.append(att_partner_id)

        mail_to = config_param.sudo().get_param("export_data_csv.mail_to")
        mail_content = {
            "subject": "Archivos CSV",
            "body_html": "Sending files: CSV MH",
            "email_from": mail_server.smtp_user,
            "email_to": mail_to,
            "attachment_ids": [(6, 0, att_ids)],
        }
        try:
            res = self.env["mail.mail"].sudo().create(mail_content).send()
        except Exception as e:
            print("Error ", e)
            pass


class ExportDataCsvLines(models.Model):
    _description = "Export Data Lines"
    _name = "export.data.csv.line"

    name = fields.Char(string="Name module")
    export_id = fields.Many2one(
        "export.data.csv",
        string="Export data",
        help="Export data that owns this line",
        ondelete="cascade",
        index=True,
    )
    last_id = fields.Char(string="Last id processed")
    record_count = fields.Integer(string="Number of records processed")
    csv_file_id = fields.Many2one(
        "ir.attachment", string="CSV file", copy=False, readonly=True
    )


class ExportModuleLines(models.Model):
    _description = "Export Module Lines"
    _name = "export.module.line"

    name = fields.Char(string="Name module")
    list_fields = fields.Text(string="List fields")
    last_id = fields.Char(string="Last id processed")
    record_count = fields.Integer(string="Number of records processed")
    export_data = fields.Boolean(string="Export data")
    last_date = fields.Datetime(string="Date")
