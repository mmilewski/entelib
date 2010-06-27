#
# TODO:
# - this tool should add project info header at the beginning of each .py file.
# - it would be nice if it checked before if such header exists
#

my $append_newline = 1;                   # should header end with a newline?
my @header = (
    "########################################",
    "# entelib project",
    "########################################"
    );
my $joined = join("\n", @header);
$joined .="\n" if $append_newline;


print "No files were changed -- tool not implemented\n";
print $joined, "\n";
