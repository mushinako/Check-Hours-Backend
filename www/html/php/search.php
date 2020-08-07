<?php
require "/home/mushinako/www/html/vendor/autoload.php";
require "/home/mushinako/www/html/php/common.php";

error_reporting(E_ALL);
ini_set('display_errors', 'Off');
ini_set('memory_limit', '256M');
// ini_set('memory_limit', '1G');

/**
 * STMN: Name of sheet of interest
 * NMBR: Row containing data
 * DATE: Column containing event date
 * EVNT: Column containing event name
 * STRC: Starting column number
 * ENDC: Ending column number
 * STRR: Starting row number (hours)
 * ENDR: Ending row number
 */
define("STNM", "Events");
// define("NMBR", 19);
define("DATE", 1);
define("EVNT", 3);
define("STRC", 30);
// define("ENDC", 420);
define("STRR", 21);
// define("ENDR", 1000);

/**
 * XDIR: XLSX directory
 * EXTX: XLSX extension
 * LOCK: File lock
 * FPLK: Filename
 * TMLK: Time lock
 * SUMM: JSON name
 * RQLG: Request Log
 */
define("XDIR", "/home/mushinako/www/files/xlsx/");
define("EXTX", "xlsm");
define("LOCK", "/home/mushinako/www/files/key/down.lock");
define("FPLK", "/home/mushinako/www/files/key/fp.lock");
define("TMLK", "/home/mushinako/www/files/key/time.lock");
define("SUMM", "/home/mushinako/www/files/key/summ.lock");
define("RQLG", "/home/mushinako/www/files/log/request/" . (new DateTime())->format("Y-m-d H.i.s.u") . ".log");

/**
 * RTMN: One-fifth of minimum random time
 * RTMX: One-fifth of maximum random time
 */
define("RTMN", 600000);
define("RTMX", 900000);

/**
 * Filter
 */
class Filter implements \PhpOffice\PhpSpreadsheet\Reader\IReadFilter {
    /**
     * Boundaries to be read, inclusive
     */
    private $firsRow = STRR;
    private $dateCol;
    private $evntCol;
    private $cols;

    /**
     * Empty constructor
     */
    public function __construct(int $nameCol) {
        $this->dateCol = colLtr(DATE);
        $this->evntCol = colLtr(EVNT);
        $this->cols = [colLtr($nameCol), colLtr($nameCol+1), colLtr($nameCol+2)];
    }

    /**
     * Determine if cell within the row limits
     *
     * @param  string $col  : Letter of column
     * @param  int    $row  : Number of row
     * @param  string $sheet: Sheet name
     * @return bool
     */
    public function readCell($col, $row, $worksheetName = "") {
        if ($row < $this->firsRow)                              return FALSE;
        if ($col === $this->dateCol || $col === $this->evntCol) return TRUE;
        if (in_array($col, $this->cols))                        return TRUE;
        return FALSE;
    }
}

/**
 * Convert number to Excel column letter
 *
 * @param  int $c: Column number
 * @return string
 */
function colLtr(int $c): string{
    if ($c <= 0) return '';

    $letter = '';

    while($c != 0){
       $p = ($c - 1) % 26;
       $c = intval(($c - $p) / 26);
       $letter = chr(65 + $p) . $letter;
    }

    return $letter;
}

/**
 * Respond to get requests
 *   Read file update time and print
 */
function get(): void {
    echo file_get_contents(TMLK) . " P" . (date("I") === "1" ? "D" : "S") . "T";
    exit;
}

/**
 * Respond to post requests
 */
function post(): void {
    // Collect requests
    file_put_contents(RQLG, serialize($_POST) . PHP_EOL);

    // Respond in JSON
    header("Content-Type: application/json");

    // Check file lock
    if (file_get_contents(LOCK)) err_update();

    // Check post validity
    if (!valid_post(["lname" => true, "fname" => true, "id" => true])) err_request();

    // Check post invalidity
    if (invalid_post()) err_failure();

    // Check ID format
    $idStr = filter_var($_POST["id"], FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    // Check ID is 9 digits
    if (!preg_match("/^\d{9}$/", $idStr)) err_request();
    // Check ID is 11 mod 13
    $id = intval($idStr);
    if ($id % 13 !== 11) err_failure();

    // Set variables to be searched for
    $fName = filter_var($_POST["fname"], FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    $lName = filter_var($_POST["lname"], FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    $cName = strtolower($lName . ", " . $fName);

    // Read JSON
    $actJ = file_get_contents(SUMM);
    $summ = file_get_contents($actJ);
    $json = json_decode($summ, TRUE);
    $jNames = filter_var_array(array_keys(array_change_key_case($json, CASE_LOWER)), FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    $jCols = array_values($json);

    // No solution failure
    if (!in_array($cName, $jNames)) {
        usleep(rand(RTMN,RTMX)+rand(RTMN,RTMX)+rand(RTMN,RTMX)+rand(RTMN,RTMX)+rand(RTMN,RTMX));
        err_failure();
    }

    // Get column
    $nIndex = array_search($cName, $jNames);
    $c = $jCols[$nIndex];

    // Try to make copy of file
    $actX = file_get_contents(FPLK);
    $tmpX = XDIR . random_string() . "." . EXTX;
    if (!copy($actX, $tmpX)) {
        if (file_exists($tmpX)) unlink($tmpX);
        err_internal();
    }
    unset($actX);

    try {
        // Setup XLSX parser
        $reader = new PhpOffice\PhpSpreadsheet\Reader\Xlsx();
        $reader->setReadDataOnly(true);
        $reader->setLoadSheetsOnly(STNM);
        $reader->setReadFilter(new Filter($c));

        // Load XLSX
        $data = $reader->load($tmpX);
        $sheet = $data->getSheet(0);
    } catch (Exception $e) {
        // Delete temporary XLSX file
        unlink($tmpX);

        throw $e;
    }

    // Delete temporary XLSX file
    unlink($tmpX);

    // Get hours
    // $serv = $sheet->getCellByColumnAndRow($c, NMBR)->getCalculatedValue();
    // $lead = $sheet->getCellByColumnAndRow($c+1, NMBR)->getCalculatedValue();
    // $fell = $sheet->getCellByColumnAndRow($c+2, NMBR)->getCalculatedValue();
    $serv = 0.0;
    $lead = 0.0;
    $fell = 0.0;

    // Get individual hour rows
    $hours = [];
    for ($r = STRR; ; ++$r) {
        // Get name
        $eName = $sheet->getCellByColumnAndRow(EVNT, $r)->getValue();

        // End of search
        if (empty($eName)) break;

        // Get date
        $eDate = $sheet->getCellByColumnAndRow(DATE, $r)->getValue();

        // Get hours
        $s = $sheet->getCellByColumnAndRow($c, $r)->getValue();
        $l = $sheet->getCellByColumnAndRow($c+1, $r)->getValue();
        $f = $sheet->getCellByColumnAndRow($c+2, $r)->getValue();

        $sBlank = empty($s);
        $lBlank = empty($l);
        $fBlank = empty($f);

        if ($sBlank && $lBlank && $fBlank) continue;

        // Add to total
        if (!$sBlank) $serv += floatval($s);
        if (!$lBlank) $lead += floatval($l);
        if (!$fBlank) $fell += floatval($f);

        $hours[] = ["date" => $eDate, "evnt" => $eName, "serv" => $s, "lead" => $l, "fell" => $f];
    }

    // Collect responses
    $res = ["serv" => round($serv, 2), "lead" => round($lead, 2), "fell" => round($fell, 2), "data" => $hours];
    file_put_contents(RQLG, serialize(["serv" => $serv, "lead" => $lead, "fell" => $fell]) . PHP_EOL, FILE_APPEND);

    // Print hours
    success($res);
}

// Respond to requests by methods
switch ($_SERVER["REQUEST_METHOD"]) {
    case "GET":
        get();
        break;
    case "POST":
        post();
        break;
    default:
        err_reqest();
        break;
}
