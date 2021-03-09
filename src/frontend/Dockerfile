# pull official base image
FROM node:15.8.0-alpine

# set working directory
WORKDIR /src/visual

# add `/app/node_modules/.bin` to $PATH
ENV PATH /src/frontend/node_modules/.bin:$PATH

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm install --silent
RUN npm install react-scripts@4.0.2 -g --silent

WORKDIR /frontend

# start app
CMD ["npm", "start"]
