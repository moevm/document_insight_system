export function debounce(func, timeout) {
    return function perform(...args) {
        let previousCall = this.lastCall;
        let currCall = Date.now();
        this.lastCall = currCall;

        if (previousCall && (currCall - previousCall <= timeout)) {
            clearTimeout(this.lastCallTimer);
        }

        this.lastCallTimer = setTimeout(() => func(...args), timeout);
    }
};