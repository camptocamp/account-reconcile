<html>
  <head>
    <style type="text/css">
.logo {
    position: absolute;
    top: 170px;
    left: -2mm;
}
.address {
    position: absolute;
    top: 145px;
    left: 25mm;
}
.recipient{
    border-collapse: collapse;
    font-size: 60%;
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
        <%doc>create a background so we ensure rotated item is not outside printable area</%doc>
        <div style="width: 100%; height: 270px; position: absolute; top: 0; left: 0;">
        </div>
        <% shop = picking.sale_id.shop_id %>
        %if shop:
            <div class="logo_position">
            <div class="logo" style="-webkit-transform:rotate(270deg);">
                ${helper.embed_logo_by_name(shop.name + '_logo', width=24, unit='mm')|n}
            </div>
            </div>
        %endif
        <% partner = picking.partner_id %>
        <% setLang(partner.lang) %>
        <div class="address">
          <div class="code">
          %if picking.offer_id.ref and picking.sale_id.name:
              ${picking.offer_id.ref}.${picking.sale_id.name}
          %else:
              ${picking.name}/${picking.origin}
          %endif
          </div>
          <table class="recipient">
            ${address(partner=partner)}
          </table>
        </div>
      %endfor

  </body>
</html>
