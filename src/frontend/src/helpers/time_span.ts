const hoursPrDay = 24;
const minutesPrHour = 60;
const secondsPrMinute = 60;

export const seconds_to_timespan_string = (seconds: number) => {
    console.log(seconds);
    let days = Math.floor(seconds / (hoursPrDay * minutesPrHour * secondsPrMinute));
    seconds -= days * hoursPrDay * minutesPrHour * secondsPrMinute;

    let hours = Math.floor(seconds / (minutesPrHour * secondsPrMinute));
    seconds -= hours * minutesPrHour * secondsPrMinute;

    let minutes = Math.floor(seconds / (secondsPrMinute));
    seconds -= minutes * secondsPrMinute;

    let day_string = days > 0 ? `${days} ${days == 1 ? "day" : "days"} ` : "";
    let hour_string = hours > 0 ? `${hours} ${hours == 1 ? "hour" : "hours"} ` : "";
    let minute_string = minutes > 0 ? `${minutes} ${minutes == 1 ? "minute" : "minutes"} ` : "";
    let second_string = seconds > 0 ? `${seconds} ${seconds == 1 ? "second" : "seconds"} ` : "";

    return `${day_string}${hour_string}${minute_string},${second_string}`;
}