interface constant_settings {
    api_url: string;
    ship_types: string[];
}

const initShipTypes = [
    "Anti-pollution",
    "Cargo",
    "Diving",
    "Dredging",
    "Fishing",
    "HSC",
    "Law enforcement",
    "Medical",
    "Military",
    "Not party to conflict",
    "Other",
    "Passenger",
    "Pilot",
    "Pleasure",
    "Port tender",
    "Reserved",
    "Sailing",
    "SAR",
    "Spare 1",
    "Spare 2",
    "Tanker",
    "Towing",
    "Towing long/wide",
    "Tug",
    "Undefined",
    "WIG",
];

const prod: constant_settings = {
    api_url: "https://api.techsource.dk",
    ship_types: initShipTypes,
};

const dev: constant_settings = {
    api_url: "http://localhost:5000",
    ship_types: initShipTypes,
};

export const config = process.env.NODE_ENV === "development" ? dev : prod;
