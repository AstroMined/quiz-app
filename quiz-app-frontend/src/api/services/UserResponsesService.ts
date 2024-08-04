/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserResponseSchema } from '../models/UserResponseSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UserResponsesService {
    /**
     * Create User Response Endpoint
     * @param requestBody
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static createUserResponseEndpointUserResponsesPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<UserResponseSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/user-responses/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Responses Endpoint
     * @param userId
     * @param questionId
     * @param startTime
     * @param endTime
     * @param skip
     * @param limit
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static getUserResponsesEndpointUserResponsesGet(
        userId?: (number | null),
        questionId?: (number | null),
        startTime?: (string | null),
        endTime?: (string | null),
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<UserResponseSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/user-responses/',
            query: {
                'user_id': userId,
                'question_id': questionId,
                'start_time': startTime,
                'end_time': endTime,
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Response Endpoint
     * @param userResponseId
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static getUserResponseEndpointUserResponsesUserResponseIdGet(
        userResponseId: number,
    ): CancelablePromise<UserResponseSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/user-responses/{user_response_id}',
            path: {
                'user_response_id': userResponseId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update User Response Endpoint
     * @param userResponseId
     * @param requestBody
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static updateUserResponseEndpointUserResponsesUserResponseIdPut(
        userResponseId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<UserResponseSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/user-responses/{user_response_id}',
            path: {
                'user_response_id': userResponseId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete User Response Endpoint
     * @param userResponseId
     * @returns void
     * @throws ApiError
     */
    public static deleteUserResponseEndpointUserResponsesUserResponseIdDelete(
        userResponseId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/user-responses/{user_response_id}',
            path: {
                'user_response_id': userResponseId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
