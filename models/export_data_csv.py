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
    line_ids = fields.One2many(
        "export.data.csv.line", "export_id", string="Export Data Lines"
    )

    @api.model
    def generate_partner_csv(self):
        """Return string with data"""
        result = {}
        cst_string = ""
        total_rows = 0
        start_id = 0
        last_id = 0
        modules = self.env["export.module.line"].search(
            [("name", "=", "partner"), ("export_data", "=", True)]
        )
        if modules:
            module = modules[0]
            start_id = module.last_id

        sql = """
        SELECT  p.id,p.name
        FROM    res_partner AS p
        WHERE p.id > %d
        ORDER BY p.id ;""" % int(
            start_id
        )

        self._cr.execute(sql)
        rows = self._cr.fetchall()
        if rows:
            cst_string = cst_string + "id" + "\t" + "name" + "\t\n"
            for row in rows:
                total_rows += 1
                last_id = row[0]
                pid = row[0]
                pname = row[1]
                cst_string = cst_string + str(pid) + "\t" + pname + "\t\n"
            result = {
                "data": cst_string,
                "module": "partner",
                "total_rows": total_rows,
                "last_id": last_id,
            }
        return result

    @api.model
    def _write_attachment(self, data, export_id, model_name):
        """ """
        line_obj = self.env["export.data.csv.line"]
        fecha = time.strftime("%Y_%m_%d_%H%M%S")
        name = "PARTNER_" + fecha + "." + "csv"

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
                "name": "Partner",
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
        data = self.generate_partner_csv()
        self._write_attachment(data, self.id, self._name)
        self.write({"state": "done"})

        return True

    def action_cron_generate_csv(self):
        now = datetime.datetime.now()
        export_obj = self.env["export.data.csv"]
        name = "Export Modules " + now.strftime("%m/%d/%Y, %H:%M:%S")
        instance = export_obj.create(
            {"name": name, "date_start": now, "state": "draft"}
        )
        data = instance.generate_partner_csv()
        instance._write_attachment(data, instance.id, instance._name)
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
        att_id = instance._write_attachment(data, instance.id, instance._name)
        instance.write({"state": "done"})
        att_ids.append(att_id)

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
