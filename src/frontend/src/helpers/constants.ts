interface constant_settings {
    api_url: string
}

const prod: constant_settings = {
    api_url: "https://api.techsource.dk"
};

const dev: constant_settings = {
    api_url: "http://localhost:5000"
};

export const config = process.env.NODE_ENV === 'development' ? dev : prod;

