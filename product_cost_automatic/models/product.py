from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_automatically = fields.Boolean(
        'Automatic', compute='_compute_is_automatically',
        inverse='_set_is_automatically', store=True)
    
    purchase_line_ids = fields.One2many('purchase.order.line',sting='Purchase Lines',compute='_compute_purchase_line_ids',inverse="_set_purchase_line_ids",)
    
    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        res.update({'is_automatically': True})
        return res
        
    @api.depends('product_variant_ids', 'product_variant_ids.purchase_line_ids')
    def _compute_purchase_line_ids(self):
        for p in self:
            if len(p.product_variant_ids) == 1:
                p.purchase_line_ids = p.product_variant_ids.purchase_line_ids
    
    def _set_purchase_line_ids(self):
        for p in self:
            if len(p.product_variant_ids) == 1:
                p.product_variant_ids.purchase_line_ids = p.purchase_line_ids
                
    @api.depends('product_variant_ids', 'product_variant_ids.is_automatically')
    def _compute_is_automatically(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.is_automatically = template.product_variant_ids.is_automatically
        for template in (self - unique_variants):
            template.is_automatically = False
            
    @api.one
    def _set_is_automatically(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.is_automatically = self.is_automatically
            
    def button_po_cost(self):
        return self.mapped('product_variant_ids').button_po_cost()
    
    
    # @api.multi
    # def _create_product_variant(self, combination, log_warning=False):
    #     self.ensure_one()
    #     Product= super(ProductTemplate, self)._create_product_variant(combination,log_warning=log_warning)
    #
    #     if not Product.is_automatically:
    #         Product.sudo().write({
    #             'is_automatically':True,
    #         })
    #     return Product
    
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_automatically = fields.Boolean(string='Automatically')
    purchase_line_ids = fields.One2many('purchase.order.line','product_id','Purchase Lines')
    
    @api.model
    def default_get(self, fields):
        res = super(ProductProduct, self).default_get(fields)
        res.update({'is_automatically': True})
        return res
    
    def button_po_cost(self):
        for product in self:
            stock_id = self.env['stock.picking'].search([('state','=','done'),('purchase_id','!=',False),('move_ids_without_package.product_id','=',product.id)], order="id desc",limit=1)
            if stock_id.purchase_id:
                for po_l in stock_id.purchase_id.order_line:
                    if po_l.product_id == product:
                        price = po_l.price_unit
                        if po_l.product_id.product_tmpl_id.uom_po_id != po_l.product_uom:
                            default_uom = po_l.product_id.product_tmpl_id.uom_po_id
                            price = po_l.product_uom._compute_price(po_l.price_unit, default_uom)
                        product.standard_price = price
            elif product.bom_count > 0:
                    product.standard_price = product._get_price_from_bom()
                
                        

    
                
