// 1. 定义基础配置（替代 client.ts 的核心逻辑）
const baseURL = import.meta.env.DIFY_BASE_URL as string
const apiKey = import.meta.env.DIFY_API_KEY as string
// 2. 定义通用类型（直接内置，无需单独 types.ts）
export interface ApiResponse<T> {
    code: number;
    message: string;
    data: T;
}

export interface PaginatedResult<T> {
    items: T[];
    total: number;
    page: number;
    limit: number;
}

// 3. 定义 dataset 相关类型
export interface Dataset {
    id: string;
    name: string;
    description: string;
    createdAt: string;
    status: 'draft' | 'published' | 'archived';
}

export interface CreateDatasetParams {
    name: string;
    description?: string;
}

// 4. 直接在接口中写请求逻辑（无需导入 client.ts）
export async function getDatasetList(page = 1, limit = 10) {
    try {
        // 拼接请求地址和参数
        const url = `${baseURL}/datasets?page=${page}&limit=${limit}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
        });

        // 处理响应
        if (!response.ok) throw new Error(`请求失败：${response.status}`);
        const resData = await response.json() as ApiResponse<PaginatedResult<Dataset>>;
        return resData.data; // 直接返回业务数据
    } catch (err) {
        const msg = err instanceof Error ? err.message : '获取数据集列表失败';
        console.error(msg);
        throw new Error(msg); // 抛出错误让调用方处理
    }
}

export async function createDataset(params: CreateDatasetParams) {
    // 前端参数校验
    if (!params.name?.trim()) throw new Error('数据集名称不能为空');

    try {
        const response = await fetch(`${baseURL}/datasets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params), // 转换请求体
        });

        if (!response.ok) throw new Error(`创建失败：${response.status}`);
        const resData = await response.json() as ApiResponse<Dataset>;
        return resData.data;
    } catch (err) {
        const msg = err instanceof Error ? err.message : '创建数据集失败';
        console.error(msg);
        throw new Error(msg);
    }
}