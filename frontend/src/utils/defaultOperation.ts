const DEFAULT_OPERATION_KEY = 'default_operation_id';

export const getDefaultOperationId = (): string | null => {
    return localStorage.getItem(DEFAULT_OPERATION_KEY);
};

export const setDefaultOperationId = (id: number): void => {
    localStorage.setItem(DEFAULT_OPERATION_KEY, id.toString());
};

export const clearDefaultOperationId = (): void => {
    localStorage.removeItem(DEFAULT_OPERATION_KEY);
};
