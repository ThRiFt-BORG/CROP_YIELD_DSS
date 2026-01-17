export interface Feature {
    name: string;
    value: number;
}

export interface TimeSeriesData {
    date: string;
    value: number;
}

export interface QueryPointResponse {
    predicted_yield: number;
    features: Feature[];
    time_series: TimeSeriesData[];
}
