/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserSchema } from '../models/UserSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UserManagementService {
    /**
     * Read Users
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static readUsersUsersGet(): CancelablePromise<Array<UserSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/',
        });
    }
    /**
     * Create User
     * @param requestBody
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static createUserUsersPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/users/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read User Me
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static readUserMeUsersMeGet(): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/me',
        });
    }
    /**
     * Update User Me
     * @param requestBody
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static updateUserMeUsersMePut(
        requestBody: Record<string, any>,
    ): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/users/me',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
