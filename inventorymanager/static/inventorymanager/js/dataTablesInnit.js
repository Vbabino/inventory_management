$(document).ready(function() {
    var table = $('#myTable').DataTable({
        buttons: [
            {
                extend: 'copy',
                className: 'btn btn-primary'  // Adding space between buttons
            },
            {
                extend: 'csv',
                className: 'btn btn-primary mx-2'
            },
            {
                extend: 'excel',
                className: 'btn btn-primary'
            },
            {
                extend: 'pdf',
                className: 'btn btn-primary mx-2'
            },
            {
                extend: 'print',
                className: 'btn btn-primary'
            }
        ],
        responsive: true,
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search...",
        },
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]]
    });

    table.buttons().container()
        .appendTo('.card-header');  // Appending buttons to the card header
});