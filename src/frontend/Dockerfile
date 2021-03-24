# pull official base image
FROM node:15.8.0-alpine

# set working directory
WORKDIR /frontend

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
COPY tsconfig.json ./
COPY public ./public/
RUN npm install --silent
RUN npm install react-scripts@4.0.3 -g --silent

# start app
CMD ["npm", "start"]
