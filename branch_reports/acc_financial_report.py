# -*- coding: utf-8 -*-
from odoo import models
from collections import defaultdict
branch_prefix = 'Br = '
analytic_prefix = 'Aa = '


class FinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _compute_amls_results(self, options_list, calling_financial_report=None, sign=1, operator=None):
        branching_for_exp = self.env.context.get('branching_for_exp')
        # if not branching_for_exp:
        #     res = super(FinancialReportLine, self)._compute_amls_results(options_list, calling_financial_report=calling_financial_report, sign=sign)
        #     return res
        self.ensure_one()
        params = []
        queries = []

        account_financial_report_html = self.financial_report_id
        horizontal_group_by_list = account_financial_report_html._get_options_groupby_fields(options_list[0])
        group_by_list = [self.groupby] + horizontal_group_by_list
        group_by_list.append('branch_id')
        group_by_list.append('analytic_account_id')
        group_by_clause = ','.join('account_move_line.%s' % gb for gb in group_by_list)
        group_by_field = self.env['account.move.line']._fields[self.groupby]

        ct_query = self.env['res.currency']._get_query_currency_table(options_list[0])
        parent_financial_report = self._get_financial_report()
        for i, options in enumerate(options_list):
            new_options = self._get_options_financial_line(options, calling_financial_report, parent_financial_report)
            line_domain = self._get_domain(new_options, parent_financial_report)
            tables, where_clause, where_params = account_financial_report_html._query_get(new_options, domain=line_domain)
            queries.append('''
                SELECT ''' + (group_by_clause and '%s,' % group_by_clause) + ''' %s AS period_index,
                COALESCE(SUM(ROUND(%s * account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance
                FROM ''' + tables + ''' JOIN ''' + ct_query + ''' ON currency_table.company_id = account_move_line.company_id
                WHERE ''' + where_clause + (group_by_clause and 'GROUP BY %s' % group_by_clause) + '''
            ''')
            params += [i, sign] + where_params
        
        results = {}
        account_balances = {}
        distinct_branch_ids = {}
        distinct_analytic_ids = {}
        bb_dicts_per_account = {}
        aab_dicts_per_branch = {}
        
        final_query = ' UNION ALL '.join(queries)
        parent_financial_report._cr_execute(options_list[0], final_query, params)
        rows = self._cr.dictfetchall()
        for res in rows:
            # Build the key.
            key = [res['period_index']]
            for gb in horizontal_group_by_list:
                key.append(res[gb])
            key = tuple(key)
            account_id = res[self.groupby]
            account_balances.setdefault(account_id, 0)
            
            bb_dicts_per_account.setdefault(account_id, {})
            cur_branch_id = res.get('branch_id') or 0
            distinct_branch_ids[cur_branch_id] = 1
            branch_balance = bb_dicts_per_account[account_id].get(cur_branch_id) or 0
            bb_dicts_per_account[account_id][cur_branch_id] = branch_balance + res['balance']

            aab_dicts_per_branch.setdefault(account_id, {})
            aab_dicts_per_branch[account_id].setdefault(cur_branch_id, {})
            cur_analytic_id = res.get('analytic_account_id') or 0
            distinct_analytic_ids[cur_analytic_id] = 1
            analytic_balance = aab_dicts_per_branch[account_id][cur_branch_id].get(cur_analytic_id) or 0
            aab_dicts_per_branch[account_id][cur_branch_id][cur_analytic_id] = analytic_balance + res['balance']
            
            results.setdefault(account_id, {})
            account_balances[account_id] += res['balance']
            results[account_id][key] = account_balances[account_id]

        branches_dict = self.get_id_object_dict(distinct_branch_ids, 'res.branch')
        analytic_account_dict = self.get_id_object_dict(distinct_analytic_ids, 'account.analytic.account')

        if group_by_field.relational:
            sorted_records = self.env[group_by_field.comodel_name].search([('id', 'in', tuple(results.keys()))])
            sorted_values = sorted_records.name_get()
        else:
            sorted_values = [(v, v) for v in sorted(list(results.keys()))]
        ar = []
        for group_by_key, display_name in sorted_values:
            ar.append((group_by_key, display_name, results[group_by_key]))
            branch_balances = bb_dicts_per_account.get(group_by_key)
            branch_balance_keys = sorted(list(branch_balances.keys()))
            if len(branch_balance_keys):
                first_key = branch_balance_keys[0]
                if len(branch_balance_keys) > 1 or first_key != 0:
                    for bid in branch_balances:
                        vl = {(0,): branch_balances[bid]}
                        ar.append((group_by_key, branch_prefix + branches_dict[bid], vl))
                        
                        analytic_balance_dict = aab_dicts_per_branch[group_by_key][bid]
                        analytic_balance_keys = sorted(list(analytic_balance_dict.keys()))
                        if len(analytic_balance_keys):
                            first_key = analytic_balance_keys[0]
                            if len(analytic_balance_keys) > 1 or first_key != 0:
                                for aa_id in analytic_balance_dict:
                                    vl = {(0,): analytic_balance_dict[aa_id]}
                                    ar.append((group_by_key, analytic_prefix + analytic_account_dict[aa_id], vl))
                                    
        return ar
    
    def get_id_object_dict(self, dict_of_ids_as_keys, model):
        tuple_of_ids_list = tuple(dict_of_ids_as_keys.keys())
        model_records = self.env[model].search([('id', 'in', tuple_of_ids_list)])
        model_values = model_records.name_get()
        if dict_of_ids_as_keys.get(0):
            model_values = [(0, 'None')] + model_values
        id_object_dict = {x[0]: x[1] for x in model_values}
        return id_object_dict


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def _create_hierarchy(self, lines, options):

        unfold_all = self.env.context.get('print_mode') and len(options.get('unfolded_lines')) == 0 or options.get('unfold_all')

        def add_to_hierarchy(lines, key, level, parent_id, hierarchy):
            val_dict = hierarchy[key]
            unfolded = val_dict['id'] in options.get('unfolded_lines') or unfold_all
            # add the group totals
            lines.append({
                'id': val_dict['id'],
                'name': val_dict['name'],
                'title_hover': val_dict['name'],
                'unfoldable': True,
                'unfolded': unfolded,
                'level': level,
                'parent_id': parent_id,
                'columns': [{'name': self.format_value(c) if isinstance(c, (int, float)) else c, 'no_format_name': c} for c in val_dict['totals']],
                'name_class': 'o_account_report_name_ellipsis top-vertical-align'
            })
            if not self._context.get('print_mode') or unfolded:
                # add every direct child group recursively
                for child in sorted(val_dict['children_codes']):
                    add_to_hierarchy(lines, child, level + 1, val_dict['id'], hierarchy)
                # add all the lines that are in this group but not in one of this group's children groups
                for l in val_dict['lines']:
                    l['level'] = level + 1
                    l['parent_id'] = val_dict['id']
                lines.extend(val_dict['lines'])

        def compute_hierarchy(lines, level, parent_id):
            # put every line in each of its parents (from less global to more global) and compute the totals
            hierarchy = defaultdict(lambda: {'totals': [None] * len(lines[0]['columns']), 'lines': [], 'children_codes': set(), 'name': '', 'parent_id': None, 'id': ''})
            for line in lines:
                account = self.env['account.account'].browse(line.get('account_id', self._get_caret_option_target_id(line.get('id'))))
                codes = self.get_account_codes(account)  # id, name
                for code in codes:
                    hierarchy[code[0]]['id'] = 'hierarchy_' + str(code[0])
                    hierarchy[code[0]]['name'] = code[1]
                    for i, column in enumerate(line['columns']):
                        line_name = line.get('name') or ''
                        if line_name.startswith(branch_prefix) or line_name.startswith(analytic_prefix):
                            continue
                        if 'no_format_name' in column:
                            no_format = column['no_format_name']
                        elif 'no_format' in column:
                            no_format = column['no_format']
                        else:
                            no_format = None
                        if isinstance(no_format, (int, float)):
                            if hierarchy[code[0]]['totals'][i] is None:
                                hierarchy[code[0]]['totals'][i] = no_format
                            else:
                                hierarchy[code[0]]['totals'][i] += no_format
                for code, child in zip(codes[:-1], codes[1:]):
                    hierarchy[code[0]]['children_codes'].add(child[0])
                    hierarchy[child[0]]['parent_id'] = hierarchy[code[0]]['id']
                hierarchy[codes[-1][0]]['lines'] += [line]
            # compute the tree-like structure by starting at the roots (being groups without parents)
            hierarchy_lines = []
            for root in [k for k, v in hierarchy.items() if not v['parent_id']]:
                add_to_hierarchy(hierarchy_lines, root, level, parent_id, hierarchy)
            return hierarchy_lines

        new_lines = []
        account_lines = []
        current_level = 0
        parent_id = 'root'
        for line in lines:
            if not (line.get('caret_options') == 'account.account' or line.get('account_id')):
                # make the hierarchy with the lines we gathered, append it to the new lines and restart the gathering
                if account_lines:
                    new_lines.extend(compute_hierarchy(account_lines, current_level + 1, parent_id))
                account_lines = []
                new_lines.append(line)
                current_level = line['level']
                parent_id = line['id']
            else:
                line_name = line.get('name') or ''
                if line_name.startswith(branch_prefix):
                    line['class'] = (line.get('class') or '') + 'cyber tab1'
                    line_name = line_name.replace(branch_prefix, '\t')
                    line['name'] = line_name
                if line_name.startswith(analytic_prefix):
                    line['class'] = (line.get('class') or '') + 'cyber tab2'
                    line_name = line_name.replace(analytic_prefix, '\t\t')
                    line['name'] = line_name
                # gather all the lines we can create a hierarchy on
                account_lines.append(line)
        # do it one last time for the gathered lines remaining
        if account_lines:
            new_lines.extend(compute_hierarchy(account_lines, current_level + 1, parent_id))
        return new_lines

    def get_html_footnotes(self, footnotes):
        html = super().get_html_footnotes(footnotes)
        html = self.__class__.add_script_style(html)
        return html

    @classmethod
    def add_script_style(cls, main_html):
        main_html = main_html.decode()
        styles = '.cyber.tab1 span:first-child{margin-left: 70px; color:blue}'
        styles += '.cyber.tab2 span:first-child{margin-left: 90px;; color:orange}'
        script_to_style = '<style id="br_tab_style">'+styles+'</style>'
        main_html += script_to_style
        main_html = bytes(main_html, 'utf-8')
        return main_html

