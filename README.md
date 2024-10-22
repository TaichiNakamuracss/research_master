# Bayesian_public_goods_game

Please Input a short description

## How to run(local)

事前に poetry、python3.8 をインストールしておいてください

```bash
poetry install
```

その後、自分の実験用コードを作った上でルートディレクトリで、以下のコマンドで otree が起動されます。 http://localhost:8001 で確認できます。

```
make run
```


## How to develop

- 新しいパッケージを追加したい時は `poetry add`
  - poetry の公式ドキュメントを予め読んでおくとよいです
- jupyter notebookの起動は `make jupyter`
- 必要なパッケージは `poetry add {package_name}` で追加して下さい
- gitのコミットはこまめにやる、メッセージを読めばだいたい何をやったかがわかるようにする
- PRは細かい単位でどんどん投げて、先生などをレビュワーに指定する


## How to run(production)

自分が作った otree 実験を実施する際は、これを cloud run にデプロイします。
デプロイする段階になったら GCP管理者に連絡してください。



### コーディングスタイルについて

- ファイル名
  - Snake case に統一
- 名前の付け方
  - 関数名などは Snake case
  - クラス名のみ Camel case
    - そのため、クラス名とファイル名は完全一致ではない（SnakeとCamelになる）
    - (例) DataHandler というクラスを作った際は data_handler.py というファイル名になる
    - このクラスをインスタンス化して使う際は data_handler = DataHandler() のような形で使う
- ファイル構成など
  - 基本的に Javaっぽいルールをベース
  - ファイルには1つのクラス
  - 関数は verb/ verb_object
  - bayesian_public_goods_game ディレクトリ内に必要なコードを追加していく
    - このディレクトリ以下でサブディレクトリをどのように切るのかについてはおまかせします
- クラス名は ... er, ... or など。主体にする
  - Class名.動詞(引数) という英語風に
