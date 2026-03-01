FROM node:20-alpine

WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm install

ENV PATH /app/node_modules/.bin:$PATH

# Expose the dev server port
EXPOSE 5173

# This ensures we use the dev server which supports HMR
CMD ["npm", "run", "dev"]