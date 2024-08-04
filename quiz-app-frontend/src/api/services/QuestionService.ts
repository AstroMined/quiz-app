/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { QuestionSchema } from '../models/QuestionSchema';
import type { QuestionUpdateSchema } from '../models/QuestionUpdateSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class QuestionService {
    /**
     * Create Question Endpoint
     * @param requestBody
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static createQuestionEndpointQuestionPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/question',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Question Endpoint
     * @param questionId
     * @param requestBody
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static getQuestionEndpointQuestionQuestionIdGet(
        questionId: number,
        requestBody: QuestionUpdateSchema,
    ): CancelablePromise<QuestionSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question/question_id}',
            query: {
                'question_id': questionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Question Endpoint
     * @param questionId
     * @param requestBody
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static updateQuestionEndpointQuestionQuestionIdPut(
        questionId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/question/{question_id}',
            path: {
                'question_id': questionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Question Endpoint
     * @param questionId
     * @returns void
     * @throws ApiError
     */
    public static deleteQuestionEndpointQuestionQuestionIdDelete(
        questionId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/question/{question_id}',
            path: {
                'question_id': questionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
