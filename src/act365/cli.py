import logging

import click

from act365.client import Act365Client  # Import the Act365Client class

logging.basicConfig(
    format="%(asctime)s %(levelname)-5s %(module)-10s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)
LOG = logging.getLogger("act635.cli")


@click.group()
@click.pass_context
@click.option(
    "--username",
    envvar="ACT365_USERNAME",
    prompt=True,
    show_envvar=True,
    help="The username for the Act365 account.",
)
@click.option(
    "--password",
    envvar="ACT365_PASSWORD",
    prompt=True,
    show_envvar=True,
    help="The password for the Act365 account.",
)
@click.option(
    "--siteid",
    envvar="ACT365_SITEID",
    prompt=True,
    show_envvar=True,
    help="The SiteID for the Act365 account.",
)
@click.option("-v", "--verbose", count=True)
def cli(ctx, username, password, siteid, verbose):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj["username"] = username
    ctx.obj["password"] = password
    ctx.obj["siteid"] = siteid
    ctx.obj["verbose"] = verbose

    # default log level is ERROR, so we set it to WARNING for -v, INFO for -vv, and DEBUG for -vvv
    loglevel = {
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }

    if verbose > 0:
        # only __package__ should be needed here :confused:
        logging.getLogger(__package__).setLevel(loglevel[verbose])
        LOG.setLevel(loglevel.get(verbose, logging.DEBUG))

        LOG.info(
            f"Verbosity set to {verbose}, logging level set to {logging.getLevelName(logging.getLogger('act635').getEffectiveLevel())}"
        )
        LOG.info(
            f"Verbosity set to {verbose}, logging level set to {logging.getLevelName(LOG.getEffectiveLevel())}"
        )

        LOG.debug(f"__name__ = {__name__}")
        LOG.debug(f"__package__ = {__package__}")
        LOG.debug(f"__file__ = {__file__}")

    pass


@click.group()
@click.pass_context
def bookings(ctx):
    ctx.ensure_object(dict)
    pass


@click.command()
@click.pass_context
@click.option(
    "--datefrom",
    default="01/01/2000",
    show_default=True,
    help="The date to list bookings from, in DD/MM/YYYY format.",
)
def list(ctx, datefrom):
    LOG.debug(
        f"List bookings, using the {ctx.obj['username']} account, for the site {ctx.obj['siteid']} from {datefrom}"
    )
    ctx.ensure_object(dict)
    click.echo(
        f"List bookings, using the {ctx.obj['username']} account, for the site {ctx.obj['siteid']} from {datefrom}"
    )
    act365_client = Act365Client(
        username=ctx.obj["username"],
        password=ctx.obj["password"],
        siteid=ctx.obj["siteid"],
    )

    bookings = act365_client.getBookings(
        siteid=ctx.obj["siteid"], datefrom=datefrom
    )

    click.echo(f"Found {len(bookings)} bookings")

    if len(bookings) > 0:
        booking_fmt = "{:<10} {:<10} {:<30} {:<18} {:<18} {:<18}"
        print(
            booking_fmt.format(
                "BookingID", "Forename", "Surname", "Start", "End", "Creation"
            )
        )

        for booking in bookings:
            click.echo(
                booking_fmt.format(
                    booking.BookingID,
                    booking.Forename,
                    booking.Surname,
                    booking.StartValidity,
                    booking.EndValidity,
                    booking.BookingCreatedTime,
                )
            )


@click.command()
@click.pass_context
@click.option(
    "--id",
    "--bookingid",
    "bookingids",
    required=True,
    multiple=True,
    help="The booking ID to delete. Multiple booking IDs can be specified by repeating the option.",
)
def delete(ctx, bookingids):
    ctx.ensure_object(dict)
    act365_client = Act365Client(
        username=ctx.obj["username"],
        password=ctx.obj["password"],
        siteid=ctx.obj["siteid"],
    )

    for bookingid in bookingids:
        response = act365_client.deleteBooking(bookingid)
        click.echo(response)


cli.add_command(bookings)
bookings.add_command(list)
bookings.add_command(delete)

if __name__ == "__main__":
    cli(obj={})
