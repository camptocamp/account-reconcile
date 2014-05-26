<html>
  <head>
    <style type="text/css">
.stamp {
    position: absolute;
    top: 7mm;
    left: 7mm;
}
.logo {
    position: absolute;
    top: 40mm;
    left: 0mm;
}
.address {
    position: absolute;
    top: 40mm;
    left: 20mm;
}
.recipient{
    border-collapse: collapse;
    font-size: 70%;
}
.code {
    margin-left: 1px;
    font-size: 50%;
}
    </style>
  </head>
  <body>
      <%page expression_filter="entity"/>

      <%def name="address(partner, commercial_partner=None)">
          <% company_partner = False %>
          %if commercial_partner:
              %if commercial_partner.id != partner.id:
                  <% company_partner = commercial_partner %>
              %endif
          %elif partner.parent_id:
              <% company_partner = partner.parent_id %>
          %endif

          %if not partner.parent_id.qoqa_bind_ids:
              %if company_partner:
                  <tr><td class="name">${company_partner.name or ''}</td></tr>
                  <tr><td>${partner.title and partner.title.name or ''} ${partner.name}</td></tr>
                  <% address_lines = partner.contact_address.split("\n")[1:] %>
              %else:
                  <tr><td class="name">${partner.title and partner.title.name or ''} ${partner.name}</td></tr>
                  <% address_lines = partner.contact_address.split("\n") %>
              %endif
          %else:
              <tr><td>${partner.title and partner.title.name or ''} ${partner.name}</td></tr>
              <% address_lines = partner.contact_address.split("\n")[1:] %>
          %endif
          %for part in address_lines:
              %if part:
                  <tr><td>${part}</td></tr>
              %endif
          %endfor
      </%def>

      %for picking in objects:
        <div class="stamp">
            ${helper.embed_image('png', company.swiss_pp_stamp_image, width=58, unit='mm')|n}
        </div>
        <% shop = picking.sale_id.shop_id %>
        %if shop:
            <div class="logo">
                ${helper.embed_image('png', shop.swiss_pp_logo, height=24, unit='mm')|n}
            </div>
        %endif
        <% partner = picking.partner_id %>
        <% setLang(partner.lang) %>
        <div class="address">
          %if picking.offer_id.ref and picking.sale_id.name and len(picking.move_lines) > 0 and picking.move_lines[0].tracking_id:
              <div class="code">
                ${picking.offer_id.ref}.${picking.sale_id.name}.${picking.move_lines[0].tracking_id.name}
              </div>
          %endif
          <table class="recipient">
            ${address(partner=partner)}
          </table>
        </div>
      %endfor

  </body>
</html>
