/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { QuestionSchema } from '../models/QuestionSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class QuestionsService {
    /**
     * Get Questions Endpoint
     * @param skip
     * @param limit
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static getQuestionsEndpointQuestionsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/questions/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
