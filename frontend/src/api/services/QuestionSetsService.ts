/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_question_set_endpoint_upload_questions__post } from '../models/Body_upload_question_set_endpoint_upload_questions__post';
import type { QuestionSetSchema } from '../models/QuestionSetSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class QuestionSetsService {
    /**
     * Upload Question Set Endpoint
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static uploadQuestionSetEndpointUploadQuestionsPost(
        formData: Body_upload_question_set_endpoint_upload_questions__post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/upload-questions/',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Questions Endpoint
     * @param skip
     * @param limit
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static readQuestionsEndpointQuestionSetGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSetSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question-set/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Question Set Endpoint
     * @param requestBody
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static createQuestionSetEndpointQuestionSetsPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSetSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/question-sets/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Question Sets Endpoint
     * @param skip
     * @param limit
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static readQuestionSetsEndpointQuestionSetsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSetSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question-sets/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Question Set Endpoint
     * @param questionSetId
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static getQuestionSetEndpointQuestionSetsQuestionSetIdGet(
        questionSetId: number,
    ): CancelablePromise<QuestionSetSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question-sets/{question_set_id}',
            path: {
                'question_set_id': questionSetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Question Set Endpoint
     * @param questionSetId
     * @param requestBody
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static updateQuestionSetEndpointQuestionSetsQuestionSetIdPut(
        questionSetId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSetSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/question-sets/{question_set_id}',
            path: {
                'question_set_id': questionSetId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Question Set Endpoint
     * @param questionSetId
     * @returns void
     * @throws ApiError
     */
    public static deleteQuestionSetEndpointQuestionSetsQuestionSetIdDelete(
        questionSetId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/question-sets/{question_set_id}',
            path: {
                'question_set_id': questionSetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
