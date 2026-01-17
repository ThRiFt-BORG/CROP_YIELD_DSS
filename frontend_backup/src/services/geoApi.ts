import axios from 'axios';
import { QueryPointResponse } from '../types/api';

// Use environment variable for API URL
const GEO_API_BASE_URL = import.meta.env.VITE_GEO_API_URL || 'http://localhost:8000/v1';

interface DateRange {
  start: string;
  end: string;
}

export async function fetchYieldData(lon: number, lat: number, dateRange: DateRange): Promise<QueryPointResponse> {
  const requestBody = {
    point: { lon, lat },
    date_range: dateRange,
  };

  const response = await axios.post<QueryPointResponse>(
    `${GEO_API_BASE_URL}/query/point`,
    requestBody
  );

  return response.data;
}
