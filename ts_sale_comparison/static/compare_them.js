odoo.define('ts_sale_comparison.compare', function (require) {
    var OriginalProductComparison = require('website_sale_comparison.comparison');
    let old_xmlDependencies = OriginalProductComparison.prototype.xmlDependencies || [];
    console.log(1006, old_xmlDependencies);
    var ProductComparison = OriginalProductComparison.include({
        xmlDependencies: old_xmlDependencies.concat(['/ts_sale_comparison/static/compare_them.xml']),
        template: 'product_compare'
    });
    return ProductComparison;
});
