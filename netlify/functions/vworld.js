const https = require('https');

exports.handler = async function(event, context) {
  const bbox = event.queryStringParameters.bbox;
  const key = 'D0F229B6-968D-3F5F-B4EB-E509962F466C';

  const url = `https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX=${bbox}&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY=${key}`;

  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          },
          body: data
        });
      });
    }).on('error', (e) => {
      resolve({
        statusCode: 500,
        body: JSON.stringify({ error: e.message })
      });
    });
  });
};
