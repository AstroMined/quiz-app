/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubjectCreateSchema } from '../models/SubjectCreateSchema';
import type { SubjectSchema } from '../models/SubjectSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SubjectsService {
    /**
     * Create Subject Endpoint
     * Create a new subject.
     *
     * Args:
     * subject (SubjectCreateSchema): The subject data to be created.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * SubjectSchema: The created subject.
     * @param requestBody
     * @returns SubjectSchema Successful Response
     * @throws ApiError
     */
    public static createSubjectEndpointSubjectsPost(
        requestBody: SubjectCreateSchema,
    ): CancelablePromise<SubjectSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/subjects/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Subject Endpoint
     * Read a subject by ID.
     *
     * Args:
     * subject_id (int): The ID of the subject to be read.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * SubjectSchema: The read subject.
     *
     * Raises:
     * HTTPException: If the subject is not found.
     * @param subjectId
     * @returns SubjectSchema Successful Response
     * @throws ApiError
     */
    public static readSubjectEndpointSubjectsSubjectIdGet(
        subjectId: number,
    ): CancelablePromise<SubjectSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Subject Endpoint
     * Update a subject by ID.
     *
     * Args:
     * subject_id (int): The ID of the subject to be updated.
     * subject (SubjectCreateSchema): The updated subject data.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * SubjectSchema: The updated subject.
     *
     * Raises:
     * HTTPException: If the subject is not found.
     * @param subjectId
     * @param requestBody
     * @returns SubjectSchema Successful Response
     * @throws ApiError
     */
    public static updateSubjectEndpointSubjectsSubjectIdPut(
        subjectId: number,
        requestBody: SubjectCreateSchema,
    ): CancelablePromise<SubjectSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Subject Endpoint
     * Delete a subject by ID.
     *
     * Args:
     * subject_id (int): The ID of the subject to be deleted.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Raises:
     * HTTPException: If the subject is not found.
     * @param subjectId
     * @returns void
     * @throws ApiError
     */
    public static deleteSubjectEndpointSubjectsSubjectIdDelete(
        subjectId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
