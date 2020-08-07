<?php
error_reporting(E_ALL);
ini_set('display_errors', 'Off');

/**
 * Generates random string
 *
 * @param  int    $len: Length of random string to be generated
 * @param  string $chr: Characters to choose from
 * @return string
 */
function random_string(int $len = 32, string $chr = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"): string {
    $chl = strlen($chr);
    $str = "";
    for ($i = 0; $i < $len; $i++) {
        $str .= $chr[mt_rand(0, $chl - 1)];
    }
    return $str;
}

/**
 * Returns the validity of the post
 *   For each key all of the following must be true for validity
 *     1. Key exists
 *     2. Key value is of type string
 *     3. If $required set, key value length at least one
 *
 * @param  array $keys: All keys to be checked, in $keyname => $required format
 * @return bool
 */
function valid_post(array $keys): bool {
    foreach ($keys as $k => $v) {
        if (!array_key_exists($k, $_POST) || !is_string($_POST[$k]) || ($v && strlen($_POST[$k]) <= 0)) {
            return false;
        }
    }
    return true;
}

/**
 * Returns the invalidity of the post
 *   For bait key any of the following can be true for invalidity
 *     1. Key does not exist
 *     2. Key value is not of type string
 *     3. Key value is not empty
 *
 * @param  string $k: Bait key name
 * @return bool
 */
function invalid_post(string $k = "pass"): bool {
    return !array_key_exists($k, $_POST) || !is_string($_POST[$k]) || strlen($_POST[$k]) !== 0;
}

/**
 * Throws an error with given error code
 *
 * @param int $code: Error code
 */
function err(int $code): void {
    echo json_encode(["stat" => $code]);
    exit;
}

/**
 * Throws an internal error (99)
 */
function err_internal(): void {
    err(99);
}

/**
 * Throws a request error (-2)
 */
function err_request(): void {
    err(-2);
}

/**
 * Throws a data-updating error (-3)
 */
function err_update(): void {
    err(-3);
}

/**
 * Throws a failure error (-1)
 */
function err_failure(): void {
    err(-1);
}

/**
 * Success
 *
 * @param array $ret: Return values
 */
function success(array $ret = []): void {
    echo json_encode(["stat" => 0] + $ret);
    exit;
}
