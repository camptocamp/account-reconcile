<html>
<head>
<style type="text/css">
${css}
.description {
  font-family: helvetica;
  font-size: 9px;
}
table.dispatch {
  width: 100%;
}
table.dispatch td {
  text-align: center;
}
table.pack {
  text-align: left;
  width: 100%;
  margin-left: 50px;
  margin-top: 30px;
  border-collapse: collapse;
}
table.pack caption {
  text-align: left;
  margin-left: -50px;
  font-weight: bold;
}
table.pack td {
  border-bottom: 1px solid;
}
</style>
</head>
<body>
<table style="border:solid 0px" width="100%">
  <tr>
      <td align="left">${_('Date')}: ${formatLang(str(date.today()), date=True)}</td>
      <td align="right">${_('Printed by')}: ${user.name}  </td>
  </tr>
</table>
<br/>
<br/>

%for dispatch in objects:
  <table style="dispatch">
    <tr>
      <td><h1>${_('Dispatch Order')} ${dispatch.name}</h1></td>
    </tr>
    <tr>
      <td>${_('Picked by')}: ${dispatch.picker_id.name if dispatch.picker_id else ''}</td>
    </tr>
  </table>
  %if dispatch.notes:
    <p>${dispatch.notes}</p>
  %endif
  %for pack, moves in get_packs(dispatch):
    <table class="pack">
      %if pack:
        <caption>${pack.serial if pack.serial else _('Pack %s has no tracking number') % pack.name}</caption>
      %else:
        <caption>${_('Not in a pack')}</caption>
      %endif
      %for move in moves:
        <tr align="left">
          <td>${move.product_id.default_code}</td>
          <td>${move.product_id.name}</td>
          <td>${move.product_id.variants}</td>
          <td>${move.product_qty} ${move.product_uom.name}</td>
          <td>${move.state}</td>
        </tr>
      %endfor
  </table>
  %endfor
  <p style="page-break-after:always">&nbsp;</p>
%endfor
</body>
</html>
