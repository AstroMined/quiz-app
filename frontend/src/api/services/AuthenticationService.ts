/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_endpoint_login_post } from '../models/Body_login_endpoint_login_post';
import type { TokenSchema } from '../models/TokenSchema';
import type { UserCreateSchema } from '../models/UserCreateSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthenticationService {
    /**
     * Login Endpoint
     * @param formData
     * @returns TokenSchema Successful Response
     * @throws ApiError
     */
    public static loginEndpointLoginPost(
        formData: Body_login_endpoint_login_post,
    ): CancelablePromise<TokenSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Logout Endpoint
     * This function logs out a user by adding their token to the revoked tokens list.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static logoutEndpointLogoutPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/logout',
        });
    }
    /**
     * Register User
     * Endpoint to register a new user.
     *
     * Args:
     * user: A UserCreate schema object containing the user's registration information.
     * db: A database session dependency injected by FastAPI.
     *
     * Raises:
     * HTTPException: If the username is already registered.
     *
     * Returns:
     * The newly created user object.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static registerUserRegisterPost(
        requestBody: UserCreateSchema,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
