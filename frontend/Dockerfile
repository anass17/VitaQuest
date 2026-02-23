FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

ENV PATH /app/node_modules/.bin:$PATH

# Expose the dev server port
EXPOSE 3000

# This ensures we use the dev server which supports HMR
CMD ["npm", "run", "dev"]