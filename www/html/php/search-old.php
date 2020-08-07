<?php
require "/home/mushinako/www/html/vendor/autoload.php";
require "/home/mushinako/www/html/php/common.php";

error_reporting(E_ALL);
ini_set('display_errors', 'Off');
ini_set('memory_limit', '1024M');

/**
 * STMN: Name of sheet of interest
 * NAME: Row containing name
 * NMBR: Row containing data
 * DATE: Column containing event date
 * EVNT: Column containing event name
 * STRC: Starting column number
 * ENDC: Ending column number
 * STRR: Starting row number (hours)
 * ENDR: Ending row number
 */
define("STNM", "Events");
define("NAME", 11);
define("NMBR", 19);
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
 * TMLK: Time locki
 * RQLG: Request Log
 */
define("XDIR", "/home/mushinako/www/files/xlsx/");
define("EXTX", "xlsm");
define("LOCK", "/home/mushinako/www/files/key/down.lock");
define("FPLK", "/home/mushinako/www/files/key/fp.lock");
define("TMLK", "/home/mushinako/www/files/key/time.lock");
define("RQLG", "/home/mushinako/www/files/log/request/" . (new DateTime())->format("Y-m-d H.i.s.u") . ".log");

/**
 * RTMN: One-fifth of minimum random time
 * RTMX: One-fifth of maximum random time
 */
define("RTMN", 900000);
define("RTMX", 1500000);

/**
 * Filter
 */
class Filter implements \PhpOffice\PhpSpreadsheet\Reader\IReadFilter {
    /**
     * First row to be read, inclusive
     */
    private $firRow  = NAME;

    /**
     * Empty constructor
     */
    public function __construct() {}

    /**
     * Determine if cell within the row limits
     *
     * @param  string $col  : Letter of column
     * @param  int    $row  : Number of row
     * @param  string $sheet: Sheet name
     * @return bool
     */
    public function readCell($col, $row, $worksheetName = "") {
        return $row >= $this->firRow;
    }
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
    if (file_get_contents(LOCK)) {
        err_update();
    }

    // Check post validity
    if (!valid_post(["lname" => true, "fname" => true, "id" => true])) {
        err_request();
    }

    // Check post invalidity
    if (invalid_post()) {
        usleep(rand(RTMN,RTMX)+rand(RTMN,RTMX)+rand(RTMN,RTMX)+rand(RTMN,RTMX)+rand(RTMN,RTMX));
        err_failure();
    }

    // Check ID format
    $idStr = filter_var($_POST["id"], FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    // Check ID is 9 digits
    if (!preg_match("/^\d{9}$/", $idStr)) {
        err_request();
    }
    // Check ID is 11 mod 13
    $id = intval($idStr);
    if ($id % 13 !== 11) {
        err_failure();
    }

    try {
        // Try to make copy of file
        $actX = file_get_contents(FPLK);
        $tmpX = XDIR . random_string() . "." . EXTX;
        if (!copy($actX, $tmpX)) {
            if (file_exists($tmpX)) {
                unlink($tmpX);
            }
            err_internal();
        }
        unset($actX, $ext);

        // Set variables to be searched for
        $fName = filter_var($_POST["fname"], FILTER_SANITIZE_FULL_SPECIAL_CHARS);
        $lName = filter_var($_POST["lname"], FILTER_SANITIZE_FULL_SPECIAL_CHARS);

        // Setup XLSX parser
        $reader = new PhpOffice\PhpSpreadsheet\Reader\Xlsx();
        $reader->setReadDataOnly(true);
        $reader->setLoadSheetsOnly(STNM);
        $reader->setReadFilter(new Filter());

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

    // Search for data
    $noRes = true;
    for ($c = STRC; ; $c += 3) {
        // Get name in lastname, firstname format
        $nName = strtolower(filter_var($sheet->getCellByColumnAndRow($c, NAME)->getValue(), FILTER_SANITIZE_FULL_SPECIAL_CHARS));

        // End of search
        if ($nName === "<member name>" || $nName === "" || $nName === NULL) {
            break;
        }

        // Split and trim lastname and firstname
        $aName = explode(",", $nName);

        // Break if match
        if (trim($aName[0]) === $lName) {
            if (!isset($aName[1])) {
                $aName[1] = null;
            }
            if ($aName[1] === null || trim($aName[1]) === $fName) {
                $noRes = false;
                break;
            }
        }
    }

    // No solution failure
    if ($noRes) {
        err_failure();
    }

    // Get hours
    $serv = $sheet->getCellByColumnAndRow($c, NMBR)->getCalculatedValue();
    $lead = $sheet->getCellByColumnAndRow($c+1, NMBR)->getCalculatedValue();
    $fell = $sheet->getCellByColumnAndRow($c+2, NMBR)->getCalculatedValue();

    // Get individual hour rows
    $hours = [];
    for ($r = STRR; ; ++$r) {
        // Get name
        $eName = $sheet->getCellByColumnAndRow(EVNT, $r)->getValue();

        // End of search
        if ($eName === "" || $eName === NULL) {
            break;
        }

        // Get date
        $eDate = $sheet->getCellByColumnAndRow(DATE, $r)->getValue();

        // Get hours
        $s = $sheet->getCellByColumnAndRow($c, $r)->getValue();
        $l = $sheet->getCellByColumnAndRow($c+1, $r)->getValue();
        $f = $sheet->getCellByColumnAndRow($c+2, $r)->getValue();

        if (($s !== "" && $s !== NULL) || ($l !== "" && $l !== NULL) || ($f !== "" && $f !== NULL)) {
            $hours[] = ["date" => $eDate, "event" => $eName, "serv" => $s, "lead" => $l, "fell" => $f];
        }
    }

    // Collect responses
    $res = ["serv" => $serv, "lead" => $lead, "fell" => $fell, "data" => $hours];
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
