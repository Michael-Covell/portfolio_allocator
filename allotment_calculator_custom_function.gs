/**
 * Custom function to get the range of values in a column above the Total row for a given header
 *
 * @param {string} headerName The name of the header in the active sheet
 * @return The range of values in the column above the Total row
 * @customfunction
 */
function HEADER_TO_COORDINATES_STR(headerName) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];

  // Find the column index based on the header name
  var columnIndex = headers.indexOf(headerName);

  if (columnIndex === -1) {
    return "Header not found";
  }

  // Get the corresponding column letter coordinate
  var columnLetter = String.fromCharCode("A".charCodeAt(0) + columnIndex);

  // Find the row number where "Total" is in column A
  var totalRow = sheet.createTextFinder("Total").findNext().getRow();

  // Calculate the row index where the range starts (1 row below the header)
  var headerRow = sheet.createTextFinder(headerName).findNext().getRow();
  var startRow = headerRow + 1;

  // Get the range of values in the column above the Total row
  var columnRangeAboveTotal = columnLetter + startRow + ":" + columnLetter + (totalRow - 1);

  return columnRangeAboveTotal;
}

/**
 * Function to return array when given an array, coordinates (as a string), or header name
 *
 * @param {string|string[]} coordinates The coordinates of the range, a header name, or an array of numbers
 * @return {string[]|number[]} An array containing values based on the input
 * @customfunction
 */
function GET_DATA(input) {
  if (!input) {
    return [];
  }

  if (Array.isArray(input) || typeof input === 'number') {
    // If the input is an array or number, return it as is
    return input;

  } else if (typeof input === 'string') {

    // If input is a string, prepare to pull data from sheet
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet()

    // Check if it's coordinates or a header name
    if (/^[A-Za-z0-9_]+![A-Z]+\d+$/.test(input) || /^[A-Z]+\d+$/.test(input)) {
      // Code for references to a cell in any sheet
      return sheet.getRange(input).getValue()
      
    } else if (/^[A-Za-z0-9_]+![A-Z]+\d+:[A-Z]+\d+$/.test(input) || /^[A-Z]+\d+:[A-Z]+\d+$/.test(input)) {
      // Code for references to a range in any sheet
      return sheet.getRange(input).getValues().flat()
      
    } else {
      // If it's not coordinates, assume it's a header name and use function
      input = HEADER_TO_COORDINATES_STR(input);
      return sheet.getRange(input).getValues().flat()
    }
    
    } else {
  
      // Handle other cases, such as when input is neither an array nor a string
      return [];
  }
}


/**
 * Custom function to calculate the sum of an array or individual values
 *
 * @param {...(number|number[])} values An array of numbers or individual values
 * @return The sum of the numbers
 * @customfunction
 */
function SUM(values) {
  // Flatten the input to handle both array and individual values
  values = [].concat(...values);

  return values.reduce(function (acc, value) {
    return acc + Number(value);
  }, 0);
}


function SUM_SELECT_VALUES(rowIndexes, array) {
  // Calculate the sum of values
  var sum = 0;
  for (var i = 0; i < rowIndexes.length; i++) {
    var rowIndex = rowIndexes[i];
    if (rowIndex >= 0 && rowIndex < array.length) {
      sum += array[rowIndex];
    }
  }

  return sum;
}

/**
 * Custom function to calculate allotments based on given parameters
 *
 * @param {number[]} cv An array of values
 * @param {number[]} t_pct An array of values
 * @param {number[]} selectRanks An array of selected ranks
 * @param {number} cash The cash value
 * @return {Object} The allotments as a dictionary
 * @customfunction
 */
function CALCULATE_ALLOTMENTS(index_range, e, cv, t_pct, selectIndices, cash) {
  var allotments = {}
  
  for (var i = index_range[0]; i < index_range[1]+1; i++) {
    if (selectIndices.indexOf(i) !== -1) {
      allotments[i] = ((e + t_pct[i]) * (SUM(cv) + cash)) - cv[i]
    } else {
      allotments[i] = 0
    }
  }

  return allotments
}

/**
 * Function to get the first and last index of an array
 *
 * @param {any[]} arr The input array
 * @return {number[]} An array containing the first and last index
 * @customfunction
 */
function GET_FIRST_LAST_INDEX(arr) {
  if (arr && arr.length > 0) {
    var firstIndex = 0;
    var lastIndex = arr.length - 1;
    return [firstIndex, lastIndex];
  } else {
    // Handle the case where the array is empty
    return [null, null]
  }
}

/**
 * Function to get indices of values greater than zero in an array
 *
 * @param {number[]} arr The input array
 * @return {number[]} An array containing the indices of values greater than zero
 * @customfunction
 */
function GET_INDICES_GREATER_THAN_ZERO(arr) {
  var indices = [];

  arr.forEach(function (value, index) {
    if (value > 0) {
      indices.push(index);
    }
  });

  return indices;
}

function non_negative_values(allotments){
  non_negative = true
  for (var key in allotments) {
    if (allotments.hasOwnProperty(key)) {
      var val = allotments[key]
      if (val < 0) {
        non_negative = false
      } 
    }
  }
  return non_negative
}

/**
 * Function to get indices where allotment values are greater than 0
 *
 * @param {Object} allotments An object containing allotment values
 * @return {string[]} An array containing indices where allotment values are greater than 0
 */
function getSelectIndices(allotments) {
  var selectIndices = [];

  for (var key in allotments) {
    if (allotments.hasOwnProperty(key) && allotments[key] > 0) {
      selectIndices.push(Number(key));
    }
  }

  return selectIndices;
}


/**
 * Custom function to check if a value is a number
 *
 * @param {*} value The value to check
 * @return {boolean} true if the value is a number, false otherwise
 * @customfunction
 */
function IS_NUMBER(value) {
  return typeof value === 'number' && !isNaN(value);
}

/**
 * Custom function to calculate allotments
 *
 * @param {string[]} cash_str string corresponding to cell with initial cash value
 * @param {string[]} deficit_str string corresponding to range of cells with deficit values (for each investment)
 * @param {string[]} cv_str string corresponding to range of cells with current values (for each investment)
 * @param {string[]} t_pct_str string corresponding to range of cells with target percent (for each investment)
 * @return {number[]} An array containing allotments
 * @customfunction 
 */
function M2(cash_str,deficit_str,cv_str,t_pct_str) {
  SpreadsheetApp.flush()

  
  var cash = GET_DATA(cash_str)
  var deficit = GET_DATA(deficit_str).flat()
  var cv = GET_DATA(cv_str).flat()
  var t_pct = GET_DATA(t_pct_str).flat()

  var index_range = GET_FIRST_LAST_INDEX(cv)
  var selectIndices = GET_INDICES_GREATER_THAN_ZERO(deficit)
  
  let allotments = {}
  var success = false
  while (!success) {
    var cv_select_sum = SUM_SELECT_VALUES(selectIndices, cv)
    var t_pct_select_sum = SUM_SELECT_VALUES(selectIndices, t_pct)
    var e = (1/selectIndices.length) * ((cv_select_sum + cash)/(SUM(cv) + cash) - t_pct_select_sum)
    
    allotments = CALCULATE_ALLOTMENTS(index_range, e, cv, t_pct, selectIndices, cash)
    if (non_negative_values(allotments)){
      var success = true
    } else{
      var selectIndices = getSelectIndices(allotments)
    }   
  }
  var dataArray = Object.values(allotments)
  return dataArray
}
/**TESTING**/

cash = 2500
current_values = [54703, 18062, 18127, 17993, 9348]
target_pcts = [.4816, .1605, .1605, .1605, .0368]
target_values = target_pcts.map(value => value * (SUM(current_values) + cash))
deficits = target_values.map((target, index) => [target - current_values[index]]);

Logger.log(M2(cash,deficits,current_values,target_pcts))
/**
 */