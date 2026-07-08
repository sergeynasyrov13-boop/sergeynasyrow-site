# Run from the repo root: docker build -f container/Dockerfile -t sergeynasyrow-site .
FROM node:20-alpine

WORKDIR /app
COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["node", "container/server.js"]
