import axios, { AxiosError } from 'axios';

const API_URL = 'http://localhost:8000/api'

// interface Symbol {
//     symbol: string;
// }

interface SignupResponse {
    message: string;
    uid: string;
}

interface ErrorResponse {
    detail: string;
}

export const signup = async (email: string, password: string) => {
    try {
        const response = await axios.post<SignupResponse>(`${API_URL}/auth/signup`, {
            email,
            password,
            initial_balance: 500000
        });
        console.log('Signup response:', response.data);
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            const axiosError = error as AxiosError<ErrorResponse>;
            console.error('Signup error:', axiosError.response?.data);
            throw new Error(axiosError.response?.data?.detail || 'Failed to sign up');
        }
        throw error;
    }
}