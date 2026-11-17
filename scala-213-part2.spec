Name:		scala-213-part2
Version:	1
Release:	1
Summary:	Second Scala 2.13.16 checkpoint, through 2.13.0-M1
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/scala/scala
Source0:	scala-2.13.16.tar.gz
Source1:	scala-official-objects.tar
Source2:	java-diff-utils-git.tar
Source3:	scala-213-drivers.tar

BuildArch:	noarch
BuildRequires:	scala-213-part1 = 1
BuildRequires:	scala-bootstrap = 2.10.7
BuildRequires:	java-1.8.0-openjdk-devel
BuildRequires:	git-core
BuildRequires:	make
BuildRequires:	python
BuildRequires:	tar
BuildRequires:	unzip

%description
Checkpoint of the Scala 2.13.16 source climb from v2.12.0-M1 through
2.13.0-M1. It resumes from the scala-213-part1 v2.11.6 pack. The
slimmed 2.13.0-M1 pack is the starr compiler for 2.13.0-M2. This
package does not provide the Scala 2.13.16 compiler.

%prep
%autosetup -n scala-2.13.16
tar -xf %{SOURCE3}
set -euo pipefail
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
test -s LICENSE
test -s compile.sh
test -s check.sh
test -s prune-stage.sh
test -s Hello.scala
test -s build-212m1.sh
test -s build-direct.sh
test -s build-direct-chain.sh
grep -q SCALA_213_FROM compile.sh
grep -q SCALA_213_SEED compile.sh
grep -q need_ant_contrib compile.sh
grep -q SCALA_213_FROM_PENDING build-direct-chain.sh
test -s scripts/scalac
test -d scala-official.git
test -s vendor/apache-ant-1.9.16/bootstrap.sh
/bin/rm -f scala-official.git/objects/info/alternates
/bin/mkdir -p scala-official.git/objects/pack
tar -xf %{SOURCE1} -C scala-official.git/objects/pack
/bin/rm -rf scala-official.git/worktrees
sed -i 's#^	url = /home/bero/.*#	url = .#' scala-official.git/config deps/scala-asm.git/config
test ! -e scala-official.git/objects/info/alternates
pack=$(find scala-official.git/objects/pack -name '*.pack' -type f)
test -s "$pack"
git --git-dir="$PWD/scala-official.git" rev-parse --verify "v2.12.0-M1^{commit}"
git --git-dir="$PWD/scala-official.git" rev-parse --verify "v2.13.0-M1^{commit}"
grep -F -q 'url = .' scala-official.git/config
grep -F -q 'url = .' deps/scala-asm.git/config
if grep -F -q /home/bero scala-official.git/config deps/scala-asm.git/config; then
	echo "host path remains in git config"
	exit 1
fi
/bin/rm -rf vendor-src/java-diff-utils
/bin/mkdir -p vendor-src/java-diff-utils
tar -xf %{SOURCE2} -C vendor-src/java-diff-utils
test -d vendor-src/java-diff-utils/.git
git -C vendor-src/java-diff-utils rev-parse --verify "java-diff-utils-parent-4.12^{commit}"
git -C vendor-src/java-diff-utils rev-parse --verify "java-diff-utils-parent-4.15^{commit}"

%build
set -eo pipefail
export JAVA_HOME=$(ls -d %{_jvmdir}/java-1.8.0-openjdk-* | head -n 1)
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
export SCALA_213_SEED=%{_datadir}/scala-213-part1/seed
export SCALA_213_FROM=v2.12.0-M1
export SCALA_213_UNTIL=2.13.0-M1
bash ./compile.sh

%install
set -eo pipefail
dest=%{buildroot}%{_datadir}/scala-213-part2/seed
stage=official-sbt/v2.13.0-M1
/bin/mkdir -p "$dest/$stage"
/bin/cp -a "$stage"/. "$dest/$stage/"
/bin/rm -rf "$dest/$stage/.git"
python3 - "$dest" << 'PY'
import os, shutil, sys
dest = sys.argv[1]
src = "deps-build"
if os.path.isdir(src):
    n = 0
    for dirpath, dirnames, filenames in os.walk(src):
        for name in filenames:
            if not name.endswith(".jar"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, src)
            target = os.path.join(dest, "deps-build", rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(full, target)
            n += 1
    print("seed_jars", n)
PY
printf '%s\n' 2.13.0-M1 > "$dest/until-stage"
printf '%s\n' 2.13.0-M2 > "$dest/next-stage"
test -s "$dest/$stage/build/pack/lib/scala-library.jar"
test -s "$dest/$stage/build/pack/lib/scala-reflect.jar"
test -s "$dest/$stage/build/pack/lib/scala-compiler.jar"
test -x "$dest/$stage/build/pack/bin/scalac"
test ! -e "$dest/$stage/src"
grep -qx 2.13.0-M1 "$dest/until-stage"
grep -qx 2.13.0-M2 "$dest/next-stage"
test -s "$dest/deps-build/scala-asm-9.7.1-scala-1/scala-asm.jar"
test -s "$dest/deps-build/java-diff-utils-4.12/java-diff-utils.jar"
test -s "$dest/deps-build/java-diff-utils-4.15/java-diff-utils.jar"

%check
set -eo pipefail
export JAVA_HOME=$(ls -d %{_jvmdir}/java-1.8.0-openjdk-* | head -n 1)
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
out=$(bash ./check.sh %{buildroot}%{_datadir}/scala-213-part2/seed/official-sbt/v2.13.0-M1/build/pack)
printf '%s\n' "$out"
test "$out" = "scala_stage_ok 42"

%files
%{_datadir}/scala-213-part2
%license LICENSE
