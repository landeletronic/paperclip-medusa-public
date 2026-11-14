import http from "node:http";

function listen(port, targetUrl, unavailableMessage) {
  const target = new URL(targetUrl);
  const proxy = http.createServer((request, response) => {
    const upstream = http.request(
      {
        hostname: target.hostname,
        port: target.port,
        method: request.method,
        path: request.url,
        headers: { ...request.headers, host: target.host },
      },
      (upstreamResponse) => {
        response.writeHead(upstreamResponse.statusCode ?? 502, upstreamResponse.headers);
        upstreamResponse.pipe(response);
      },
    );

    upstream.on("error", () => {
      if (!response.headersSent) response.writeHead(502);
      response.end(unavailableMessage);
    });
    request.pipe(upstream);
  });

  proxy.on("clientError", (_error, socket) => {
    socket.end("HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n");
  });
  proxy.listen(port, "127.0.0.1");
}

listen(4001, "http://litellm:4000", "LiteLLM local indisponível");
listen(8643, "http://hermes-agent:8642", "Hermes local indisponível");
