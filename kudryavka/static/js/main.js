(function($) {
    $(function() {
        $('.toggle').on('click', function(e) {
            e.preventDefault();
            $('.navbar').toggleClass('hidden', 'shown');
        });
    });
})(jQuery);
